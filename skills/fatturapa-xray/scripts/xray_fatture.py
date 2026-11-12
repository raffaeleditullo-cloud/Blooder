#!/usr/bin/env python3
"""
FatturaPA X-Ray — Motore deterministico di analisi Fatturazione Elettronica Italiana (FPR12 / FPA12).
100% Python Standard Library (zero dipendenze esterne).

Funzioni principali:
1. Apertura trasparente di file .xml e buste firmate .xml.p7m (CAdES DER/BER anche chunked + Base64).
2. Gestione rigorosa TipoDocumento (TD04 / TD08 Note di Credito sottratte con segno -1).
3. Rilevamento rincari silenziosi dei fornitori riga per riga (confronto storico PrezzoUnitario).
4. Rilevamento abbonamenti ricorrenti e possibili fatture duplicate.
5. Audit Anti-Scarto SdI (codici 00400, 00401, 00445 sottocodici Natura N2/N3/N6, 00423, 00419, 00311, Bollo 77,47 EUR).
6. Calcolo Salvadanaio Tasse, IVA e Netto Reale (Regime Forfettario per ATECO vs Regime Ordinario).
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

CENT = Decimal("0.01")
BOLLO_THRESHOLD = Decimal("77.47")
BOLLO_AMOUNT = Decimal("2.00")
BOLLO_NATURA_SET = {"N2.1", "N2.2", "N3.5", "N3.6", "N4"}
OBSOLETE_NATURA_PARENTS = {"N2", "N3", "N6"}
VALID_NATURA_CODES = {
    "N1",
    "N2.1", "N2.2",
    "N3.1", "N3.2", "N3.3", "N3.4", "N3.5", "N3.6",
    "N4",
    "N5",
    "N6.1", "N6.2", "N6.3", "N6.4", "N6.5", "N6.6", "N6.7", "N6.8", "N6.9",
    "N7",
}
CREDIT_NOTE_TYPES = {"TD04", "TD08"}

ATECO_PRESETS = {
    "artigiani": Decimal("86"),      # es. 43.xx installazione serramenti / impiantisti
    "professionisti": Decimal("78"), # es. consulenti, tecnici, studi
    "software": Decimal("67"),       # es. 62.xx / 63.xx sviluppo software, agenzie
    "commercio": Decimal("40"),      # vendita al dettaglio / ingrosso / ristorazione
}


def d(val: str | int | float | Decimal | None, default: str = "0.00") -> Decimal:
    if val is None:
        return Decimal(default)
    if isinstance(val, Decimal):
        return val
    cleaned = str(val).strip().replace(",", ".")
    if not cleaned:
        return Decimal(default)
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal(default)


def q2(val: Decimal) -> Decimal:
    return val.quantize(CENT, rounding=ROUND_HALF_UP)


def fmt_eur(val: Decimal) -> str:
    quant = q2(val)
    sign = "-" if quant < 0 else ""
    s = f"{abs(quant):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sign}{s} €"


# ==========================================================
# SBUCCIATORE .XML E .XML.P7M (CAdES DER / BER / BASE64)
# ==========================================================

def _strip_asn1_Wrapper_if_needed(raw: bytes) -> bytes:
    """Estrae l'XML pulito da un file normale o da una busta firmata CAdES (.p7m)."""
    # 1. Prova decodifica Base64 se il file .p7m è salvato in PEM / Base64 testuale
    stripped = raw.strip()
    if stripped.startswith(b"-----BEGIN"):
        lines = [ln for ln in stripped.splitlines() if not ln.startswith(b"-----")]
        try:
            raw = base64.b64decode(b"".join(lines))
        except Exception:
            pass
    elif b"<" not in raw[:200]:
        # Potrebbe essere Base64 puro senza header PEM
        compact = re.sub(rb"\s+", b"", stripped)
        if len(compact) > 64 and re.fullmatch(rb"[A-Za-z0-9+/=]+", compact):
            try:
                decoded = base64.b64decode(compact)
                if b"FatturaElettronica" in decoded:
                    raw = decoded
            except Exception:
                pass

    # 2. Se è già XML pulito (con eventuale BOM UTF-8)
    bom_clean = raw.lstrip(b"\xef\xbb\xbf\r\n\t ")
    if bom_clean.startswith(b"<?xml") or bom_clean.startswith(b"<"):
        end_match = re.search(rb"</(?:[A-Za-z0-9_]+:)?FatturaElettronica\s*>", bom_clean)
        if end_match:
            return bom_clean[: end_match.end()]
        return bom_clean

    # 3. Estrazione da busta binaria PKCS#7 / CAdES (anche con OCTET STRING spezzettati BER)
    start_match = re.search(rb"<\?xml|<(?:\w+:)?FatturaElettronica\b", raw)
    end_match = None
    for m in re.finditer(rb"</(?:\w+:)?FatturaElettronica\s*>", raw):
        end_match = m

    if not start_match or not end_match or end_match.end() <= start_match.start():
        raise ValueError("Impossibile individuare il nodo <FatturaElettronica> nel file.")

    candidate = raw[start_match.start() : end_match.end()]
    # Rimuove eventuali byte di controllo BER chunking (\x04 + lunghezza) iniettati tra blocchi OCTET STRING
    try:
        ET.fromstring(_decode_xml_bytes(candidate))
        return candidate
    except ET.ParseError:
        cleaned = bytearray()
        i = 0
        n = len(candidate)
        while i < n:
            b_val = candidate[i]
            if b_val == 0x04 and i + 2 < n:
                length_byte = candidate[i + 1]
                if length_byte < 0x80:
                    i += 2
                    continue
                elif length_byte in (0x81, 0x82):
                    skip = 2 + (length_byte - 0x80)
                    i += skip
                    continue
            if b_val >= 0x20 or b_val in (0x09, 0x0A, 0x0D) or b_val >= 0x80:
                cleaned.append(b_val)
            i += 1
        return bytes(cleaned)


def _decode_xml_bytes(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _strip_ns(elem: ET.Element) -> ET.Element:
    for el in elem.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    return elem


def _txt(parent: ET.Element | None, path: str, default: str = "") -> str:
    if parent is None:
        return default
    found = parent.find(path)
    if found is None or found.text is None:
        return default
    return found.text.strip()


# ==========================================================
# MODELLI DATI FATTURA E RIGA
# ==========================================================

@dataclass
class InvoiceLine:
    numero_linea: str
    codice_articolo: str
    descrizione: str
    quantita: Decimal
    unita_misura: str
    prezzo_unitario: Decimal
    sconto_magg_factor: Decimal
    prezzo_totale: Decimal
    aliquota_iva: Decimal
    natura: str
    tipo_cessione: str


@dataclass
class VatSummary:
    aliquota_iva: Decimal
    natura: str
    imponibile: Decimal
    imposta: Decimal
    esigibilita: str


@dataclass
class ParsedInvoice:
    filename: str
    formato_trasmissione: str
    codice_destinatario: str
    pec_destinatario: str
    cedente_piva: str
    cedente_cf: str
    cedente_nome: str
    cessionario_piva: str
    cessionario_cf: str
    cessionario_nome: str
    tipo_documento: str
    data: str
    numero: str
    importo_totale_doc: Decimal
    bollo_virtuale: str
    importo_bollo: Decimal
    ritenuta_importo: Decimal
    cassa_imponibile: Decimal
    cassa_importo: Decimal
    cassa_aliquota_iva: Decimal
    cassa_natura: str
    lines: list[InvoiceLine] = field(default_factory=list)
    vat_summaries: list[VatSummary] = field(default_factory=list)
    scadenze: list[tuple[str, Decimal, str]] = field(default_factory=list)

    @property
    def sign(self) -> int:
        return -1 if self.tipo_documento in CREDIT_NOTE_TYPES else 1

    @property
    def sum_imponibile(self) -> Decimal:
        return sum((v.imponibile for v in self.vat_summaries), Decimal("0.00"))

    @property
    def sum_imposta(self) -> Decimal:
        return sum((v.imposta for v in self.vat_summaries), Decimal("0.00"))

    @property
    def computed_gross(self) -> Decimal:
        total = self.sum_imponibile + self.sum_imposta
        if self.bollo_virtuale.upper() == "SI":
            # Il bollo può essere già addebitato in riga N1 o solo in DatiBollo
            has_bollo_line = any(
                ln.natura == "N1" and abs(ln.prezzo_totale - self.importo_bollo) <= CENT
                for ln in self.lines
            )
            if not has_bollo_line:
                total += self.importo_bollo
        return q2(total)

    @property
    def effective_gross(self) -> Decimal:
        return self.importo_totale_doc if self.importo_totale_doc > 0 else self.computed_gross


def _party_name(anagrafica: ET.Element | None) -> str:
    if anagrafica is None:
        return "Sconosciuto"
    denom = _txt(anagrafica, "Denominazione")
    if denom:
        return denom
    nome = _txt(anagrafica, "Nome")
    cognome = _txt(anagrafica, "Cognome")
    full = f"{nome} {cognome}".strip()
    return full or "Sconosciuto"


def parse_fatturapa(path: Path) -> ParsedInvoice:
    raw = path.read_bytes()
    xml_bytes = _strip_asn1_Wrapper_if_needed(raw)
    xml_text = _decode_xml_bytes(xml_bytes)
    root = _strip_ns(ET.fromstring(xml_text))

    header = root.find("FatturaElettronicaHeader")
    body = root.find("FatturaElettronicaBody")
    if header is None or body is None:
        raise ValueError("Struttura FatturaPA incompleta (manca Header o Body).")

    trasm = header.find("DatiTrasmissione")
    cedente = header.find("CedentePrestatore/DatiAnagrafici")
    cessionario = header.find("CessionarioCommittente/DatiAnagrafici")

    dati_gen_doc = body.find("DatiGenerali/DatiGeneraliDocumento")
    dati_beni = body.find("DatiBeniServizi")

    cassa_el = dati_gen_doc.find("DatiCassaPrevidenziale") if dati_gen_doc is not None else None

    lines: list[InvoiceLine] = []
    if dati_beni is not None:
        for det in dati_beni.findall("DettaglioLinee"):
            qty_raw = _txt(det, "Quantita")
            qty = d(qty_raw, "1.00") if qty_raw else Decimal("1.00")
            p_unit = d(_txt(det, "PrezzoUnitario"), "0.00")
            p_tot = d(_txt(det, "PrezzoTotale"), "0.00")

            # Calcolo fattore sconto/maggiorazione composto
            factor = Decimal("1")
            for sm in det.findall("ScontoMaggiorazione"):
                tipo_sm = _txt(sm, "Tipo").upper()
                perc = d(_txt(sm, "Percentuale"), "0")
                imp = d(_txt(sm, "Importo"), "0")
                if perc > 0:
                    if tipo_sm == "SC":
                        factor *= (Decimal("1") - perc / Decimal("100"))
                    elif tipo_sm == "MG":
                        factor *= (Decimal("1") + perc / Decimal("100"))
                elif imp > 0 and p_unit != 0:
                    if tipo_sm == "SC":
                        factor *= (p_unit - imp) / p_unit
                    elif tipo_sm == "MG":
                        factor *= (p_unit + imp) / p_unit

            cod_val = ""
            cod_el = det.find("CodiceArticolo")
            if cod_el is not None:
                cod_val = _txt(cod_el, "CodiceValore")

            lines.append(
                InvoiceLine(
                    numero_linea=_txt(det, "NumeroLinea", "?"),
                    codice_articolo=cod_val,
                    descrizione=_txt(det, "Descrizione"),
                    quantita=qty,
                    unita_misura=_txt(det, "UnitaMisura"),
                    prezzo_unitario=p_unit,
                    sconto_magg_factor=factor,
                    prezzo_totale=p_tot,
                    aliquota_iva=d(_txt(det, "AliquotaIVA"), "0.00"),
                    natura=_txt(det, "Natura").upper(),
                    tipo_cessione=_txt(det, "TipoCessionePrestazione").upper(),
                )
            )

    summaries: list[VatSummary] = []
    if dati_beni is not None:
        for riep in dati_beni.findall("DatiRiepilogo"):
            summaries.append(
                VatSummary(
                    aliquota_iva=d(_txt(riep, "AliquotaIVA"), "0.00"),
                    natura=_txt(riep, "Natura").upper(),
                    imponibile=d(_txt(riep, "ImponibileImporto"), "0.00"),
                    imposta=d(_txt(riep, "Imposta"), "0.00"),
                    esigibilita=_txt(riep, "EsigibilitaIVA", "I").upper(),
                )
            )

    scadenze: list[tuple[str, Decimal, str]] = []
    for pag in body.findall("DatiPagamento"):
        for det_p in pag.findall("DettaglioPagamento"):
            scadenze.append(
                (
                    _txt(det_p, "DataScadenzaPagamento"),
                    d(_txt(det_p, "ImportoPagamento"), "0.00"),
                    _txt(det_p, "ModalitaPagamento"),
                )
            )

    return ParsedInvoice(
        filename=path.name,
        formato_trasmissione=_txt(trasm, "FormatoTrasmissione", "FPR12").upper(),
        codice_destinatario=_txt(trasm, "CodiceDestinatario"),
        pec_destinatario=_txt(trasm, "PECDestinatario"),
        cedente_piva=_txt(cedente, "IdFiscaleIVA/IdCodice"),
        cedente_cf=_txt(cedente, "CodiceFiscale"),
        cedente_nome=_party_name(cedente.find("Anagrafica") if cedente is not None else None),
        cessionario_piva=_txt(cessionario, "IdFiscaleIVA/IdCodice"),
        cessionario_cf=_txt(cessionario, "CodiceFiscale"),
        cessionario_nome=_party_name(cessionario.find("Anagrafica") if cessionario is not None else None),
        tipo_documento=_txt(dati_gen_doc, "TipoDocumento", "TD01").upper(),
        data=_txt(dati_gen_doc, "Data"),
        numero=_txt(dati_gen_doc, "Numero"),
        importo_totale_doc=d(_txt(dati_gen_doc, "ImportoTotaleDocumento"), "0.00"),
        bollo_virtuale=_txt(dati_gen_doc, "DatiBollo/BolloVirtuale").upper(),
        importo_bollo=d(_txt(dati_gen_doc, "DatiBollo/ImportoBollo"), "0.00"),
        ritenuta_importo=d(_txt(dati_gen_doc, "DatiRitenuta/ImportoRitenuta"), "0.00"),
        cassa_imponibile=d(_txt(cassa_el, "ImponibileCassa"), "0.00"),
        cassa_importo=d(_txt(cassa_el, "ImportoContributoCassa"), "0.00"),
        cassa_aliquota_iva=d(_txt(cassa_el, "AliquotaIVA"), "0.00"),
        cassa_natura=_txt(cassa_el, "Natura").upper(),
        lines=lines,
        vat_summaries=summaries,
        scadenze=scadenze,
    )


# ==========================================================
# MOTORE 1: CONTROLLO ANTI-SCARTO SDI & REGOLE FISCALI
# ==========================================================

def audit_sdi_invoice(inv: ParsedInvoice) -> list[dict]:
    issues: list[dict] = []

    def add(severity: str, code: str, message: str) -> None:
        issues.append({
            "file": inv.filename,
            "numero": inv.numero,
            "data": inv.data,
            "emittente": inv.cedente_nome,
            "gravita": severity,  # CRITICO (Scarto SdI) | FISCALE (Sanzione) | AVVISO
            "codice": code,
            "dettaglio": message,
        })

    # 1. Codice Destinatario (Errore SdI 00311)
    expected_len = 6 if inv.formato_trasmissione == "FPA12" else 7
    if len(inv.codice_destinatario) != expected_len:
        add(
            "CRITICO",
            "SdI-00311",
            f"CodiceDestinatario '{inv.codice_destinatario}' lungo {len(inv.codice_destinatario)} caratteri "
            f"(richiesti esattamente {expected_len} per formato {inv.formato_trasmissione}). La fattura verrà SCARTATA dallo SdI.",
        )

    # 2. Controllo righe: Aliquota 0 vs Natura + Sottocodici obbligatori + Quadratura riga
    bollo_subject_amount = Decimal("0.00")
    grouped_lines: dict[tuple[Decimal, str], Decimal] = defaultdict(lambda: Decimal("0.00"))

    for ln in inv.lines:
        grouped_lines[(ln.aliquota_iva, ln.natura)] += ln.prezzo_totale

        if ln.aliquota_iva == Decimal("0.00") and not ln.natura:
            add(
                "CRITICO",
                "SdI-00400",
                f"Riga {ln.numero_linea} ('{ln.descrizione[:40]}'): AliquotaIVA a 0,00% ma manca il campo <Natura> (es. N2.2 per forfettario). Scarto SdI garantito.",
            )
        elif ln.aliquota_iva > Decimal("0.00") and ln.natura:
            add(
                "CRITICO",
                "SdI-00401",
                f"Riga {ln.numero_linea}: presente sia AliquotaIVA ({ln.aliquota_iva}%) sia Natura ({ln.natura}). Scarto SdI garantito.",
            )
        elif ln.natura in OBSOLETE_NATURA_PARENTS:
            add(
                "CRITICO",
                "SdI-00445",
                f"Riga {ln.numero_linea}: codice Natura '{ln.natura}' obsoleto senza sottocodice (usa es. N2.1/N2.2, N3.1..N3.6, N6.1..N6.9). Scarto SdI.",
            )
        elif ln.natura and ln.natura not in VALID_NATURA_CODES:
            add(
                "CRITICO",
                "SdI-NATURA",
                f"Riga {ln.numero_linea}: codice Natura '{ln.natura}' non riconosciuto dal tracciato FatturaPA.",
            )

        if (
            ln.natura in BOLLO_NATURA_SET
            or ln.natura in OBSOLETE_NATURA_PARENTS
            or (ln.aliquota_iva == Decimal("0.00") and not ln.natura)
        ):
            bollo_subject_amount += ln.prezzo_totale

        expected_line_tot = q2(ln.quantita * ln.prezzo_unitario * ln.sconto_magg_factor)
        if abs(expected_line_tot - ln.prezzo_totale) > Decimal("0.02"):
            add(
                "CRITICO",
                "SdI-00423",
                f"Riga {ln.numero_linea} ('{ln.descrizione[:35]}'): PrezzoTotale dichiarato {fmt_eur(ln.prezzo_totale)} "
                f"non quadra con Quantità ({ln.quantita}) × PrezzoUnitario ({fmt_eur(ln.prezzo_unitario)}) = {fmt_eur(expected_line_tot)}. Scarto SdI.",
            )

    if inv.cassa_importo > 0:
        grouped_lines[(inv.cassa_aliquota_iva, inv.cassa_natura)] += inv.cassa_importo
        if inv.cassa_natura in BOLLO_NATURA_SET:
            bollo_subject_amount += inv.cassa_importo

    # 3. Controllo Riepilogo IVA (00419 / 00422)
    for vs in inv.vat_summaries:
        expected_vat = q2(vs.imponibile * vs.aliquota_iva / Decimal("100"))
        if abs(expected_vat - vs.imposta) > Decimal("0.02"):
            add(
                "CRITICO",
                "SdI-00421",
                f"Riepilogo IVA ({vs.aliquota_iva}%): Imposta dichiarata {fmt_eur(vs.imposta)} diversa da {fmt_eur(expected_vat)}. Scarto SdI.",
            )
        line_sum = q2(grouped_lines.get((vs.aliquota_iva, vs.natura), Decimal("0.00")))
        if abs(line_sum - vs.imponibile) > Decimal("0.05"):
            add(
                "CRITICO",
                "SdI-00422",
                f"Riepilogo IVA ({vs.aliquota_iva}% {vs.natura}): Imponibile {fmt_eur(vs.imponibile)} non coincide con la somma righe {fmt_eur(line_sum)}.",
            )

    # 4. Marca da Bollo Virtuale sopra 77,47 € (DM 17/06/2014)
    if bollo_subject_amount > BOLLO_THRESHOLD and inv.bollo_virtuale != "SI":
        add(
            "FISCALE",
            "BOLLO-7747",
            f"Importo esente/fuori campo IVA pari a {fmt_eur(bollo_subject_amount)} (> 77,47 €), "
            f"ma manca <BolloVirtuale>SI</BolloVirtuale> da 2,00 €! Rischio sanzione Agenzia delle Entrate.",
        )

    return issues


# ==========================================================
# MOTORE 2: RINCARI SILENZIOSI, ABBONAMENTI & DOPPIONI
# ==========================================================

def _normalize_item_key(ln: InvoiceLine) -> str:
    if ln.codice_articolo:
        return f"COD:{ln.codice_articolo.upper()}"
    clean = re.sub(r"\b(rif\.?|ddt|del|nr\.?|lotto)\s*[\w/-]+", "", ln.descrizione.lower())
    clean = re.sub(r"[^a-z0-9àèéìòù]+", " ", clean).strip()
    return f"DESC:{clean[:60]}"


def detect_supplier_anomalies(
    passive_invoices: list[ParsedInvoice],
    hike_threshold_pct: Decimal = Decimal("3.0"),
) -> tuple[list[dict], list[dict], list[dict]]:
    sorted_inv = sorted(passive_invoices, key=lambda x: (x.data, x.numero))

    # Storico prezzi: (fornitore_id, item_key) -> lista osservazioni
    price_history: dict[tuple[str, str], list[dict]] = defaultdict(list)
    # Storico fatture per abbonamenti e duplicati
    seen_doc_numbers: dict[tuple[str, str], ParsedInvoice] = {}
    monthly_totals_by_supplier: dict[tuple[str, Decimal], list[ParsedInvoice]] = defaultdict(list)

    duplicates: list[dict] = []

    for inv in sorted_inv:
        supp_id = inv.cedente_piva or inv.cedente_cf or inv.cedente_nome

        # Controllo fatture duplicate (stesso fornitore + stesso numero documento, file diversi)
        doc_key = (supp_id, inv.numero.strip().upper())
        if doc_key in seen_doc_numbers:
            prev_doc = seen_doc_numbers[doc_key]
            duplicates.append({
                "fornitore": inv.cedente_nome,
                "numero": inv.numero,
                "data": inv.data,
                "importo": str(q2(inv.effective_gross)),
                "file_1": prev_doc.filename,
                "file_2": inv.filename,
                "motivo": "Stesso fornitore e stesso numero fattura presente due volte nella cartella (esclusa dai totali per evitare doppio conteggio).",
            })
            continue
        seen_doc_numbers[doc_key] = inv

        if inv.tipo_documento not in CREDIT_NOTE_TYPES and inv.effective_gross > 0:
            monthly_totals_by_supplier[(supp_id, q2(inv.effective_gross))].append(inv)

        # Ignora note di credito nello storico listino prezzi per non falsare i rincari
        if inv.tipo_documento in CREDIT_NOTE_TYPES:
            continue

        for ln in inv.lines:
            if ln.prezzo_unitario <= 0 or ln.tipo_cessione in ("SC", "AB"):
                continue
            if ln.natura == "N1" and abs(ln.prezzo_unitario - BOLLO_AMOUNT) <= CENT:
                continue
            eff_unit_price = q2(ln.prezzo_unitario * ln.sconto_magg_factor)
            item_key = _normalize_item_key(ln)
            price_history[(supp_id, item_key)].append({
                "fornitore": inv.cedente_nome,
                "articolo": ln.descrizione,
                "codice": ln.codice_articolo,
                "data": inv.data,
                "numero_fattura": inv.numero,
                "file": inv.filename,
                "prezzo_unitario": eff_unit_price,
                "quantita": ln.quantita,
            })

    # Calcolo rincari silenziosi
    price_hikes: list[dict] = []
    for (_, _), obs_list in price_history.items():
        if len(obs_list) < 2:
            continue
        baseline = obs_list[0]
        prev = baseline
        for curr in obs_list[1:]:
            if prev["prezzo_unitario"] > 0:
                diff = curr["prezzo_unitario"] - prev["prezzo_unitario"]
                pct = (diff / prev["prezzo_unitario"]) * Decimal("100")
                if pct >= hike_threshold_pct:
                    extra_on_invoice = q2(diff * curr["quantita"])
                    price_hikes.append({
                        "fornitore": curr["fornitore"],
                        "articolo": curr["articolo"],
                        "codice": curr["codice"],
                        "prezzo_precedente": str(prev["prezzo_unitario"]),
                        "data_precedente": prev["data"],
                        "prezzo_nuovo": str(curr["prezzo_unitario"]),
                        "data_nuova": curr["data"],
                        "fattura_nuova": curr["numero_fattura"],
                        "aumento_pct": str(q2(pct)),
                        "sovrapprezzo_su_fattura": str(extra_on_invoice),
                    })
            prev = curr

    # Rilevamento addebiti fissi ricorrenti (abbonamenti / canoni ripetuti)
    recurring: list[dict] = []
    for (_, amount), inv_group in monthly_totals_by_supplier.items():
        unique_dates = {i.data[:7] for i in inv_group if len(i.data) >= 7}
        if len(inv_group) >= 2 and len(unique_dates) >= 2:
            sample_desc = inv_group[0].lines[0].descrizione if inv_group[0].lines else "Canone / Servizio"
            recurring.append({
                "fornitore": inv_group[0].cedente_nome,
                "importo_fisso_lordo": str(amount),
                "occorrenze": len(inv_group),
                "mesi_rilevati": sorted(unique_dates),
                "descrizione_tipo": sample_desc,
                "spesa_cumulata": str(q2(amount * Decimal(len(inv_group)))),
            })

    return price_hikes, recurring, duplicates


# ==========================================================
# MOTORE 3: SALVADANAIO TASSE, IVA & NETTO REALE
# ==========================================================

def compute_tax_cashflow(
    active_invoices: list[ParsedInvoice],
    passive_invoices: list[ParsedInvoice],
    regime: str = "forfettario",
    coeff_redditivita: Decimal = Decimal("86"),
    aliquota_imposta_pct: Decimal = Decimal("15"),
    aliquota_inps_pct: Decimal = Decimal("24"),
) -> dict:
    # Fatture attive (con sottrazione automatica Note di Credito TD04/TD08!)
    fatturato_imponibile = sum((i.sign * i.sum_imponibile for i in active_invoices), Decimal("0.00"))
    iva_debito = sum(
        (i.sign * v.imposta for i in active_invoices for v in i.vat_summaries if v.esigibilita != "S"),
        Decimal("0.00"),
    )
    incasso_lordo_atteso = sum((i.sign * (i.effective_gross - i.ritenuta_importo) for i in active_invoices), Decimal("0.00"))

    # Fatture passive (acquisti fornitori, sottratte le Note di Credito TD04/TD08!)
    costi_imponibili = sum((i.sign * i.sum_imponibile for i in passive_invoices), Decimal("0.00"))
    iva_credito = sum((i.sign * i.sum_imposta for i in passive_invoices), Decimal("0.00"))
    uscite_fornitori_lorde = sum((i.sign * i.effective_gross for i in passive_invoices), Decimal("0.00"))

    credit_notes_passive = sum((1 for i in passive_invoices if i.tipo_documento in CREDIT_NOTE_TYPES))
    credit_notes_active = sum((1 for i in active_invoices if i.tipo_documento in CREDIT_NOTE_TYPES))

    if regime.lower() == "forfettario":
        # Regola fondamentale italiana: nel Forfettario l'IVA sugli acquisti NON è detraibile (è costo vivo!),
        # e le imposte/INPS si calcolano su Fatturato × Coefficiente di redditività ATECO (non sui costi reali).
        reddito_imponibile_lordo = q2(max(Decimal("0.00"), fatturato_imponibile) * (coeff_redditivita / Decimal("100")))
        contributi_inps_stimati = q2(reddito_imponibile_lordo * (aliquota_inps_pct / Decimal("100")))
        base_imposta_sostitutiva = q2(max(Decimal("0.00"), reddito_imponibile_lordo - contributi_inps_stimati))
        imposta_sostitutiva = q2(base_imposta_sostitutiva * (aliquota_imposta_pct / Decimal("100")))
        salvadanaio_fisco_totale = q2(contributi_inps_stimati + imposta_sostitutiva)
        saldo_iva_da_versare = q2(max(Decimal("0.00"), iva_debito))  # dovrebbe essere 0 in forfettario regolare
        netto_reale_tasca = q2(incasso_lordo_atteso - uscite_fornitori_lorde - salvadanaio_fisco_totale - saldo_iva_da_versare)

        return {
            "regime": "Forfettario",
            "coefficiente_ateco_pct": str(coeff_redditivita),
            "fatture_attive_lette": len(active_invoices),
            "note_credito_attive_sottratte": credit_notes_active,
            "fatture_passive_lette": len(passive_invoices),
            "note_credito_passive_sottratte": credit_notes_passive,
            "incasso_lordo_attive": str(q2(incasso_lordo_atteso)),
            "uscite_reali_fornitori_iva_inclusa": str(q2(uscite_fornitori_lorde)),
            "reddito_forfettario_imponibile": str(reddito_imponibile_lordo),
            "accantonamento_inps": str(contributi_inps_stimati),
            "accantonamento_imposta_sostitutiva": str(imposta_sostitutiva),
            "salvadanaio_tasse_inps_totale": str(salvadanaio_fisco_totale),
            "netto_vero_spendibile": str(netto_reale_tasca),
        }

    # Regime Ordinario / Semplificato
    saldo_iva = q2(iva_debito - iva_credito)
    utile_operativo_imponibile = q2(fatturato_imponibile - costi_imponibili)
    tasse_inps_stimate = q2(
        max(Decimal("0.00"), utile_operativo_imponibile) * ((aliquota_imposta_pct + aliquota_inps_pct) / Decimal("100"))
    )
    iva_da_accantonare = max(Decimal("0.00"), saldo_iva)
    netto_reale_tasca = q2(
        incasso_lordo_atteso - uscite_fornitori_lorde - iva_da_accantonare - tasse_inps_stimate
    )

    return {
        "regime": "Ordinario / Semplificato",
        "fatture_attive_lette": len(active_invoices),
        "note_credito_attive_sottratte": credit_notes_active,
        "fatture_passive_lette": len(passive_invoices),
        "note_credito_passive_sottratte": credit_notes_passive,
        "fatturato_imponibile_netto_iva": str(q2(fatturato_imponibile)),
        "costi_imponibili_netto_iva": str(q2(costi_imponibili)),
        "iva_a_debito": str(q2(iva_debito)),
        "iva_a_credito_detraibile": str(q2(iva_credito)),
        "saldo_iva_stato": str(saldo_iva),
        "utile_operativo_pre_tasse": str(utile_operativo_imponibile),
        "salvadanaio_tasse_inps_stimato": str(tasse_inps_stimate),
        "netto_vero_spendibile": str(netto_reale_tasca),
    }


# ==========================================================
# ORCHESTRATORE E FORMATTAZIONE REPORT
# ==========================================================

def collect_invoice_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    files: list[Path] = []
    for p in sorted(target.rglob("*")):
        name_low = p.name.lower()
        if p.is_file() and (name_low.endswith(".xml") or name_low.endswith(".xml.p7m")):
            # Ignora notifiche SdI (NS, RC, MC, EC, DT, SE) che non sono fatture
            if re.search(r"_(ns|rc|mc|ec|dt|se|at)_", name_low):
                continue
            files.append(p)
    return files


def render_markdown_report(result: dict) -> str:
    out: list[str] = []
    meta = result["riepilogo_scansione"]
    cash = result["salvadanaio_e_netto"]
    hikes = result["rincari_fornitori"]
    rec = result["abbonamenti_ricorrenti"]
    dups = result["possibili_doppioni"]
    sdi = result["controllo_anti_scarto_sdi"]

    out.append("# Raggi X Fatturazione Elettronica Italiana (FatturaPA)")
    out.append("")
    out.append(
        f"- **File analizzati:** `{meta['totale_file']}` "
        f"(di cui `{meta['buste_p7m_aperte']}` firmati `.xml.p7m` aperti automaticamente)"
    )
    out.append(
        f"- **Fatture Emesse (Attive):** `{cash['fatture_attive_lette']}` "
        f"| **Fatture Ricevute (Passive):** `{cash['fatture_passive_lette']}` "
        f"(Note di credito `TD04` sottratte in automatico: `{cash['note_credito_passive_sottratte'] + cash['note_credito_attive_sottratte']}`)"
    )
    out.append("")

    # 1. Salvadanaio e Netto
    out.append(f"## 1. Salvadanaio Tasse & Netto Vero ({cash['regime']})")
    if cash["regime"] == "Forfettario":
        out.append(f"- **Incassi da fatture emesse:** **{fmt_eur(d(cash['incasso_lordo_attive']))}**")
        out.append(f"- **Spese reali fornitori (IVA inclusa indetraibile):** `-{fmt_eur(d(cash['uscite_reali_fornitori_iva_inclusa']))}`")
        out.append(
            f"- **Da accantonare subito per Tasse + INPS** *(coeff. ATECO {cash['coefficiente_ateco_pct']}%)*: "
            f"`-{fmt_eur(d(cash['salvadanaio_tasse_inps_totale']))}` "
            f"*(INPS: {fmt_eur(d(cash['accantonamento_inps']))} + Imposta: {fmt_eur(d(cash['accantonamento_imposta_sostitutiva']))})*"
        )
        out.append(f"- **NETTO VERO SPENDIBILE IN TASCA:** **{fmt_eur(d(cash['netto_vero_spendibile']))}**")
    else:
        out.append(f"- **Fatturato imponibile (senza IVA):** **{fmt_eur(d(cash['fatturato_imponibile_netto_iva']))}**")
        out.append(f"- **Costi fornitori imponibili:** `-{fmt_eur(d(cash['costi_imponibili_netto_iva']))}`")
        out.append(
            f"- **Bilancio IVA Stato:** Debito `{fmt_eur(d(cash['iva_a_debito']))}` vs Credito `{fmt_eur(d(cash['iva_a_credito_detraibile']))}` "
            f"-> **Saldo IVA:** `{fmt_eur(d(cash['saldo_iva_stato']))}`"
        )
        out.append(f"- **Salvadanaio Tasse/INPS stimato:** `-{fmt_eur(d(cash['salvadanaio_tasse_inps_stimato']))}`")
        out.append(f"- **LIQUIDITÀ NETTA VERA SPENDIBILE:** **{fmt_eur(d(cash['netto_vero_spendibile']))}**")
    out.append("")

    # 2. Rincari silenziosi
    out.append(f"## 2. Rincari Silenziosi dei Fornitori ({len(hikes)} rilevati)")
    if not hikes:
        out.append("Nessun rincaro anomalo rilevato sui prezzi unitari storici.")
    else:
        out.append("| Fornitore | Articolo | Prezzo Prima | Prezzo Nuovo | Rincaro % | Extra pagato |")
        out.append("| :--- | :--- | ---: | ---: | ---: | ---: |")
        for h in hikes:
            art = f"{h['articolo']} (`{h['codice']}`)" if h["codice"] else h["articolo"]
            out.append(
                f"| {h['fornitore']} | {art} | {fmt_eur(d(h['prezzo_precedente']))} *({h['data_precedente']})* "
                f"| **{fmt_eur(d(h['prezzo_nuovo']))}** *({h['data_nuova']})* "
                f"| **+{h['aumento_pct']}%** | +{fmt_eur(d(h['sovrapprezzo_su_fattura']))} |"
            )
    out.append("")

    # 3. Controllo Anti-Scarto SdI
    out.append(f"## 3. Controllo Anti-Scarto SdI & Rischi Sanzioni ({len(sdi)} segnalazioni)")
    if not sdi:
        out.append("Tutte le fatture superano i controlli formali SdI, quadratura IVA e Marca da Bollo.")
    else:
        for issue in sdi:
            out.append(
                f"- **[{issue['gravita']} — `{issue['codice']}`]** Fattura `{issue['numero']}` ({issue['file']}): {issue['dettaglio']}"
            )
    out.append("")

    # 4. Abbonamenti e doppioni
    out.append(f"## 4. Canoni Ricorrenti ({len(rec)}) & Possibili Doppioni ({len(dups)})")
    if rec:
        for r in rec:
            out.append(
                f"- **Canone fisso ricorrente:** `{r['fornitore']}` — {fmt_eur(d(r['importo_fisso_lordo']))} × {r['occorrenze']} mesi "
                f"({', '.join(r['mesi_rilevati'])}) = **{fmt_eur(d(r['spesa_cumulata']))}** *({r['descrizione_tipo']})*"
            )
    if dups:
        for dp in dups:
            out.append(
                f"- **ATTENZIONE FATTURA DOPPIA:** `{dp['fornitore']}` n. `{dp['numero']}` da {fmt_eur(d(dp['importo']))} "
                f"presente sia in `{dp['file_1']}` sia in `{dp['file_2']}`!"
            )
    if not rec and not dups:
        out.append("Nessun abbonamento ricorrente né fattura duplicata rilevati.")

    return "\n".join(out) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="FatturaPA X-Ray — Analisi Fatture Elettroniche XML / XML.P7M")
    parser.add_argument("percorso", help="Cartella o singolo file .xml / .xml.p7m da analizzare")
    parser.add_argument("--piva", default="", help="La tua Partita IVA o CF per distinguere Attive da Passive")
    parser.add_argument("--regime", choices=["forfettario", "ordinario"], default="forfettario")
    parser.add_argument("--ateco", choices=list(ATECO_PRESETS.keys()), default="artigiani", help="Preset coeff. forfettario")
    parser.add_argument("--coeff", default="", help="Coefficiente redditività personalizzato (es. 78)")
    parser.add_argument("--imposta-pct", default="15", help="Aliquota imposta sostitutiva (5 o 15) o IRPEF media")
    parser.add_argument("--inps-pct", default="24", help="Aliquota INPS stimata sul reddito imponibile")
    parser.add_argument("--soglia-rincaro", default="3.0", help="Soglia minima % per segnalare rincari fornitori")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Formato output (md o json)")
    args = parser.parse_args()

    target = Path(args.percorso)
    if not target.exists():
        print(f"Errore: percorso non trovato -> {target}", file=sys.stderr)
        return 1

    files = collect_invoice_files(target)
    if not files:
        print(f"Nessun file .xml o .xml.p7m trovato in {target}", file=sys.stderr)
        return 1

    parsed_all: list[ParsedInvoice] = []
    parse_errors: list[dict] = []
    p7m_count = 0

    for f in files:
        if f.name.lower().endswith(".p7m"):
            p7m_count += 1
        try:
            parsed_all.append(parse_fatturapa(f))
        except Exception as exc:
            parse_errors.append({"file": f.name, "errore": str(exc)})

    my_id = re.sub(r"^IT", "", args.piva.strip().upper())
    if not my_id and parsed_all:
        # Se non specificata, deduce il soggetto titolare che compare in tutte le fatture (come cedente o cessionario)
        freq: dict[str, int] = defaultdict(int)
        for inv in parsed_all:
            for candidate in {inv.cedente_piva, inv.cessionario_piva}:
                if candidate:
                    freq[candidate.upper()] += 1
        if freq:
            my_id = max(freq.items(), key=lambda kv: kv[1])[0]

    active_inv: list[ParsedInvoice] = []
    passive_inv: list[ParsedInvoice] = []
    for inv in parsed_all:
        if my_id and (inv.cedente_piva.upper() == my_id or inv.cedente_cf.upper() == my_id):
            active_inv.append(inv)
        else:
            passive_inv.append(inv)

    price_hikes, recurring, duplicates = detect_supplier_anomalies(
        passive_inv, hike_threshold_pct=d(args.soglia_rincaro, "3.0")
    )

    dup_filenames = {dp["file_2"] for dp in duplicates}
    passive_unique = [inv for inv in passive_inv if inv.filename not in dup_filenames]

    sdi_issues: list[dict] = []
    for inv in active_inv + passive_unique:
        sdi_issues.extend(audit_sdi_invoice(inv))

    coeff = d(args.coeff) if args.coeff else ATECO_PRESETS[args.ateco]
    cashflow = compute_tax_cashflow(
        active_invoices=active_inv,
        passive_invoices=passive_unique,
        regime=args.regime,
        coeff_redditivita=coeff,
        aliquota_imposta_pct=d(args.imposta_pct, "15"),
        aliquota_inps_pct=d(args.inps_pct, "24"),
    )

    result = {
        "riepilogo_scansione": {
            "totale_file": len(files),
            "fatture_valide": len(parsed_all),
            "buste_p7m_aperte": p7m_count,
            "piva_titolare_rilevata": my_id,
            "errori_lettura": parse_errors,
        },
        "salvadanaio_e_netto": cashflow,
        "rincari_fornitori": price_hikes,
        "controllo_anti_scarto_sdi": sdi_issues,
        "abbonamenti_ricorrenti": recurring,
        "possibili_doppioni": duplicates,
    }

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_markdown_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
