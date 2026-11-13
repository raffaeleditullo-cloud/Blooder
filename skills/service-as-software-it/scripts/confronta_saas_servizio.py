"""
confronta_saas_servizio.py — Motore deterministico per Service-as-a-Software Italia (Blooderskill)
Applica la tesi Sequoia Capital ("Services are the new software") alla fiscalità italiana reale
(Regime Forfettario 5%/15% + INPS oppure Regime Ordinario/SRL) confrontando al centesimo:
  - Modello A: Vendita abbonamento Software SaaS fai-da-te (prezzo basso, alto abbandono, sforzo cliente)
  - Modello B: Vendita Servizio Finito Chiavi in Mano erogato internamente con AI (alto incasso, zero attrito)

Zero dipendenze esterne (Python 3.10+ libreria standard, Decimal ROUND_HALF_UP).
"""

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

ATECO_PRESETS = {
    "software": Decimal("0.67"),
    "professionisti": Decimal("0.78"),
    "servizi_imprese": Decimal("0.67"),
    "artigiani": Decimal("0.86"),
    "commercio": Decimal("0.40"),
}


def q2(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcola_netto_italiano(
    ricavi_lordi_mese: Decimal,
    costi_vivi_mese: Decimal,
    regime: str,
    coeff_ateco: Decimal,
    aliquota_forfettario: Decimal,
    aliquota_inps: Decimal,
    aliquota_ordinario_tot: Decimal,
) -> dict:
    if ricavi_lordi_mese <= Decimal("0"):
        return {
            "ricavi_mese": Decimal("0.00"),
            "costi_vivi_mese": q2(costi_vivi_mese),
            "tasse_inps_mese": Decimal("0.00"),
            "netto_tasca_mese": q2(-costi_vivi_mese),
        }

    if regime == "forfettario":
        # Nel Forfettario tasse e INPS si calcolano su Ricavi * Coeff ATECO; i costi vivi non riducono l'imponibile ma escono dalla tasca!
        imponibile_lordo = ricavi_lordi_mese * coeff_ateco
        contributi_inps = q2(imponibile_lordo * aliquota_inps)
        imponibile_fiscale = max(Decimal("0"), imponibile_lordo - contributi_inps)
        imposta_sost = q2(imponibile_fiscale * aliquota_forfettario)
        tasse_tot = contributi_inps + imposta_sost
        netto = q2(ricavi_lordi_mese - costi_vivi_mese - tasse_tot)
    else:
        # Regime Ordinario / SRL semplificata di confronto: le imposte si applicano sull'utile operativo (Ricavi - Costi deducibili)
        utile_operativo = ricavi_lordi_mese - costi_vivi_mese
        tasse_tot = q2(utile_operativo * aliquota_ordinario_tot) if utile_operativo > Decimal("0") else Decimal("0.00")
        netto = q2(utile_operativo - tasse_tot)

    return {
        "ricavi_mese": q2(ricavi_lordi_mese),
        "costi_vivi_mese": q2(costi_vivi_mese),
        "tasse_inps_mese": q2(tasse_tot),
        "netto_tasca_mese": netto,
    }


def trova_clienti_per_target(
    target_netto_mese: Decimal,
    prezzo_cliente: Decimal,
    costo_variabile_cliente: Decimal,
    costi_fissi_mese: Decimal,
    regime: str,
    coeff_ateco: Decimal,
    aliquota_forfettario: Decimal,
    aliquota_inps: Decimal,
    aliquota_ordinario_tot: Decimal,
) -> int:
    for n in range(1, 50001):
        ricavi = prezzo_cliente * Decimal(n)
        costi = costi_fissi_mese + (costo_variabile_cliente * Decimal(n))
        res = calcola_netto_italiano(
            ricavi, costi, regime, coeff_ateco,
            aliquota_forfettario, aliquota_inps, aliquota_ordinario_tot,
        )
        if res["netto_tasca_mese"] >= target_netto_mese:
            return n
    return -1


def main() -> None:
    p = argparse.ArgumentParser(description="Confronta Modello SaaS vs Modello Service-as-a-Software con tasse italiane reali.")
    p.add_argument("--target-netto", type=str, default="3000", help="Obiettivo netto mensile pulito in tasca in EUR (default: 3000)")
    p.add_argument("--saas-prezzo", type=str, default="39", help="Prezzo mensile abbonamento SaaS fai-da-te in EUR (default: 39)")
    p.add_argument("--saas-churn-pct", type=str, default="9", help="Abbandono mensile % clienti SaaS PMI (default: 9%%)")
    p.add_argument("--saas-api-cliente", type=str, default="1.50", help="Costo cloud/API per cliente SaaS al mese in EUR")
    p.add_argument("--saas-minuti-supporto", type=str, default="15", help="Minuti umani medi assistenza/onboarding al mese per cliente SaaS")

    p.add_argument("--servizio-prezzo", type=str, default="390", help="Prezzo mensile Servizio Finito Chiavi in Mano in EUR (default: 390)")
    p.add_argument("--servizio-churn-pct", type=str, default="3", help="Abbandono mensile % clienti Servizio Finito (default: 3%%)")
    p.add_argument("--servizio-api-cliente", type=str, default="4.50", help="Costo token/API AI per erogare il servizio a 1 cliente al mese in EUR")
    p.add_argument("--minuti-manuali-prima", type=str, default="240", help="Minuti che richiedeva il lavoro fatto a mano senza AI")
    p.add_argument("--minuti-umani-con-ai", type=str, default="25", help="Minuti umani di controllo/regia al mese per cliente usando AI")

    p.add_argument("--costi-fissi", type=str, default="80", help="Costi fissi mensili infrastruttura/tool in EUR (default: 80)")
    p.add_argument("--ore-lavoro-mese", type=str, default="140", help="Ore massime lavorabili al mese da 1 persona (default: 140)")
    p.add_argument("--regime", choices=["forfettario", "ordinario"], default="forfettario")
    p.add_argument("--ateco", choices=list(ATECO_PRESETS.keys()), default="servizi_imprese")
    p.add_argument("--imposta-forf-pct", type=str, default="5", help="5 per start-up primi 5 anni, 15 standard")
    p.add_argument("--inps-pct", type=str, default="26.07", help="Aliquota INPS Gestione Separata %% (default: 26.07)")
    p.add_argument("--tasse-ordinario-pct", type=str, default="43", help="Carico fiscale complessivo stimato %% su utile in Ordinario")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = p.parse_args()

    target_netto = Decimal(args.target_netto)
    costi_fissi = Decimal(args.costi_fissi)
    ore_max = Decimal(args.ore_lavoro_mese)
    coeff = ATECO_PRESETS[args.ateco]
    imp_forf = Decimal(args.imposta_forf_pct) / Decimal("100")
    inps_rate = Decimal(args.inps_pct) / Decimal("100")
    ord_rate = Decimal(args.tasse_ordinario_pct) / Decimal("100")
    stripe_pct = Decimal("0.015")
    stripe_fix = Decimal("0.25")

    # Costi variabili unitari (API + incasso carta Stripe UE 1.5% + 0.25€)
    saas_p = Decimal(args.saas_prezzo)
    saas_var = q2(Decimal(args.saas_api_cliente) + (saas_p * stripe_pct) + stripe_fix)
    saas_min = Decimal(args.saas_minuti_supporto)
    saas_churn = Decimal(args.saas_churn_pct) / Decimal("100")

    serv_p = Decimal(args.servizio_prezzo)
    serv_var = q2(Decimal(args.servizio_api_cliente) + (serv_p * stripe_pct) + stripe_fix)
    serv_min = Decimal(args.minuti_umani_con_ai)
    min_prima = Decimal(args.minuti_manuali_prima)
    serv_churn = Decimal(args.servizio_churn_pct) / Decimal("100")

    # Limite Forfettario Italia: 85.000 EUR / anno = 7.083,33 EUR / mese di incassato!
    soglia_forf_mese = Decimal("85000") / Decimal("12")

    n_saas = trova_clienti_per_target(target_netto, saas_p, saas_var, costi_fissi, args.regime, coeff, imp_forf, inps_rate, ord_rate)
    n_serv = trova_clienti_per_target(target_netto, serv_p, serv_var, costi_fissi, args.regime, coeff, imp_forf, inps_rate, ord_rate)

    saas_econ = calcola_netto_italiano(saas_p * n_saas, costi_fissi + saas_var * n_saas, args.regime, coeff, imp_forf, inps_rate, ord_rate)
    serv_econ = calcola_netto_italiano(serv_p * n_serv, costi_fissi + serv_var * n_serv, args.regime, coeff, imp_forf, inps_rate, ord_rate)

    saas_ore_mese = q2((Decimal(n_saas) * saas_min) / Decimal("60"))
    serv_ore_mese = q2((Decimal(n_serv) * serv_min) / Decimal("60"))

    saas_nuovi_mese_per_churn = q2(Decimal(n_saas) * saas_churn)
    serv_nuovi_mese_per_churn = q2(Decimal(n_serv) * serv_churn)

    cap_clienti_servizio_1_persona = int((ore_max * Decimal("60")) // serv_min) if serv_min > 0 else 9999
    risparmio_tempo_pct = q2(((min_prima - serv_min) / min_prima) * Decimal("100")) if min_prima > 0 else Decimal("0")

    euro_ora_saas = q2(saas_econ["netto_tasca_mese"] / saas_ore_mese) if saas_ore_mese > 0 else Decimal("0")
    euro_ora_serv = q2(serv_econ["netto_tasca_mese"] / serv_ore_mese) if serv_ore_mese > 0 else Decimal("0")

    avvisi = []
    if args.regime == "forfettario":
        if saas_econ["ricavi_mese"] > soglia_forf_mese:
            avvisi.append(f"ATTENZIONE SaaS: {saas_econ['ricavi_mese']} €/mese supera il tetto Forfettario italiano di 85.000 €/anno (7.083 €/mese).")
        if serv_econ["ricavi_mese"] > soglia_forf_mese:
            avvisi.append(f"ATTENZIONE Servizio: {serv_econ['ricavi_mese']} €/mese supera il tetto Forfettario italiano di 85.000 €/anno (7.083 €/mese).")
    if n_serv > cap_clienti_servizio_1_persona:
        avvisi.append(f"ATTENZIONE Capacità: servono {n_serv} clienti ma 1 persona da sola ne gestisce massimo {cap_clienti_servizio_1_persona} ({ore_max} ore/mese).")

    report = {
        "obiettivo_netto_mensile_eur": str(q2(target_netto)),
        "regime_fiscale": args.regime,
        "modello_a_saas": {
            "prezzo_mensile_eur": str(q2(saas_p)),
            "clienti_attivi_necessari": n_saas,
            "nuovi_clienti_ogni_mese_solo_per_coprire_abbandoni": str(saas_nuovi_mese_per_churn),
            "ricavi_lordi_mese_eur": str(saas_econ["ricavi_mese"]),
            "costi_vivi_mese_eur": str(saas_econ["costi_vivi_mese"]),
            "tasse_e_inps_mese_eur": str(saas_econ["tasse_inps_mese"]),
            "netto_reale_tasca_eur": str(saas_econ["netto_tasca_mese"]),
            "ore_umane_mese": str(saas_ore_mese),
            "netto_orario_effettivo_eur": str(euro_ora_saas),
        },
        "modello_b_service_as_software": {
            "prezzo_mensile_eur": str(q2(serv_p)),
            "clienti_attivi_necessari": n_serv,
            "nuovi_clienti_ogni_mese_solo_per_coprire_abbandoni": str(serv_nuovi_mese_per_churn),
            "ricavi_lordi_mese_eur": str(serv_econ["ricavi_mese"]),
            "costi_vivi_mese_eur": str(serv_econ["costi_vivi_mese"]),
            "tasse_e_inps_mese_eur": str(serv_econ["tasse_inps_mese"]),
            "netto_reale_tasca_eur": str(serv_econ["netto_tasca_mese"]),
            "ore_umane_mese": str(serv_ore_mese),
            "netto_orario_effettivo_eur": str(euro_ora_serv),
            "taglio_tempo_grazie_ad_ai_pct": str(risparmio_tempo_pct),
            "capacita_massima_clienti_1_operatore": cap_clienti_servizio_1_persona,
        },
        "rapporto_clienti_saas_su_servizio": round(n_saas / n_serv, 1) if n_serv > 0 else 0,
        "avvisi_fiscali_e_operativi": avvisi,
    }

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print(f"# Confronto Deterministico: SaaS Fai-da-Te vs Service-as-a-Software (Obiettivo: {q2(target_netto)} € netti/mese)")
    print(f"- **Regime fiscale simulato:** `{args.regime}` (ATECO `{args.ateco}`, costi fissi `{q2(costi_fissi)} €/mese`)")
    print(f"- **Compressione lavoro con AI:** da `{min_prima}` min a `{serv_min}` min per cliente (`-{risparmio_tempo_pct}%` di tempo umano)\n")
    print("| Voce | Modello A — SaaS Fai-da-Te | Modello B — Servizio Finito con AI |")
    print("| :--- | :---: | :---: |")
    print(f"| **Prezzo al cliente** | `{q2(saas_p)} €/mese` | **`{q2(serv_p)} €/mese`** |")
    print(f"| **Clienti attivi da trovare e tenere** | `{n_saas} clienti` | **`{n_serv} clienti`** (`{report['rapporto_clienti_saas_su_servizio']}x` più facile!) |")
    print(f"| **Clienti persi da rimpiazzare ogni mese** | `{saas_nuovi_mese_per_churn} / mese` | **`{serv_nuovi_mese_per_churn} / mese`** |")
    print(f"| **Fatturato lordo mensile** | `{saas_econ['ricavi_mese']} €` | `{serv_econ['ricavi_mese']} €` |")
    print(f"| **Costi vivi (API + Stripe + Fissi)** | `{saas_econ['costi_vivi_mese']} €` | `{serv_econ['costi_vivi_mese']} €` |")
    print(f"| **Tasse + INPS da accantonare** | `{saas_econ['tasse_inps_mese']} €` | `{serv_econ['tasse_inps_mese']} €` |")
    print(f"| **NETTO PULITO IN TASCA** | **`{saas_econ['netto_tasca_mese']} €`** | **`{serv_econ['netto_tasca_mese']} €`** |")
    print(f"| **Ore di lavoro umano al mese** | `{saas_ore_mese} ore` | **`{serv_ore_mese} ore`** (tetto max 1 persona: `{cap_clienti_servizio_1_persona}` clienti) |")
    print(f"| **Guadagno netto orario reale** | `{euro_ora_saas} €/ora` | **`{euro_ora_serv} €/ora`** |")

    if avvisi:
        print("\n### Avvisi Fiscali & Operativi")
        for a in avvisi:
            print(f"- {a}")


if __name__ == "__main__":
    main()
