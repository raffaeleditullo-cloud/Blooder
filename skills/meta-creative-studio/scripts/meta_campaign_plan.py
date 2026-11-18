"""Generatore deterministico di piano campagna Meta Ads, UTM e checklist sito (Lovable/WordPress)."""

from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

OBJECTIVE_MAP = {
    "lead": {
        "meta_objective": "Contatti (Leads)",
        "conversion_event": "Lead / Contact (o Modulo Istantaneo Meta)",
        "optimization_goal": "Massimizza il numero di contatti",
        "warning": "Verifica che l'evento Lead scatti solo sulla pagina /grazie o al submit riuscito, non al click sul bottone.",
    },
    "vendite": {
        "meta_objective": "Vendite (Sales)",
        "conversion_event": "Purchase (Acquisto) o InitiateCheckout",
        "optimization_goal": "Massimizza il numero di conversioni",
        "warning": "Assicurati che il Pixel/CAPI invii valore e valuta (EUR) su ogni acquisto.",
    },
    "traffico": {
        "meta_objective": "Traffico (Traffic)",
        "conversion_event": "Visualizzazioni della pagina di destinazione",
        "optimization_goal": "Visualizzazioni della pagina di destinazione (mai solo Clic sul link)",
        "warning": "Non usare Traffico se il vero obiettivo sono contatti o vendite: porta clic poco qualificati.",
    },
    "notorieta": {
        "meta_objective": "Notorietà (Awareness)",
        "conversion_event": "Copertura / ThruPlay",
        "optimization_goal": "Copertura o Visualizzazioni video ThruPlay",
        "warning": "Usalo solo per copertura locale o retargeting video, non per generare lead diretti.",
    },
}

SITE_CHECKLIST = {
    "lovable": [
        "Hero chiara sopra la piega con H1, sottotitolo e CTA primaria ben visibile su mobile",
        "Sezioni ordinate: Problema -> Soluzione -> Prove/Numeri -> Offerta -> FAQ -> Form",
        "Form collegato a webhook/email + redirect o stato di conferma tracciabile (/grazie)",
        "Meta Pixel / Google Tag verificato su dominio pubblicato (non solo su preview)",
        "Controllo responsive reale su viewport 375px (iPhone) e 1440px (Desktop)",
    ],
    "wordpress": [
        "Slug URL corto e pulito + Meta Title (<=60 caratteri) e Meta Description (<=155 caratteri)",
        "Immagini convertite in WebP (<200 KB) con alt text compilato",
        "Test reale di invio form + pagina /grazie dedicata con evento Pixel Lead",
        "Cache/ottimizzazione verificata dopo le modifiche (test in finestra anonima)",
        "Controllo mobile su Elementor/Gutenberg (margini, font leggibili >=16px, CTA visibile)",
    ],
}

CREATIVE_SPECS = [
    {"formato": "Post Feed IG/FB (Consigliato)", "ratio": "4:5", "pixel": "1080x1350", "note": "Massimo spazio verticale nel feed mobile"},
    {"formato": "Stories & Reels", "ratio": "9:16", "pixel": "1080x1920", "note": "Lascia 250px liberi in alto e 350px in basso"},
    {"formato": "Carosello / Quadrato", "ratio": "1:1", "pixel": "1080x1080", "note": "Coerente su tutte le schede del carosello"},
]


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    return cleaned or "campagna_meta"


def build_utm_url(base_url: str, campaign_slug: str, content_tag: str) -> str:
    parsed = urlparse(base_url.strip())
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update({
        "utm_source": "meta",
        "utm_medium": "paid_social",
        "utm_campaign": campaign_slug,
        "utm_content": content_tag,
    })
    return urlunparse(parsed._replace(query=urlencode(query)))


def build_plan(
    nome: str,
    obiettivo: str,
    budget_giornaliero: Decimal,
    giorni: int,
    url: str,
    piattaforma_sito: str,
) -> dict:
    if budget_giornaliero <= 0:
        raise ValueError("Il budget giornaliero deve essere maggiore di 0.")
    if giorni <= 0:
        raise ValueError("Il numero di giorni deve essere maggiore di 0.")

    slug = slugify(nome)
    totale = (budget_giornaliero * Decimal(giorni)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    budget_core = (budget_giornaliero * Decimal("0.70")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    budget_test = (budget_giornaliero - budget_core).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    obj_info = OBJECTIVE_MAP[obiettivo]

    return {
        "campagna": nome,
        "slug_utm": slug,
        "obiettivo_chiave": obiettivo,
        "meta_ads_setup": {
            "livello_campagna": {
                "obiettivo": obj_info["meta_objective"],
                "strategia_budget": "CBO (Advantage+ Campaign Budget)" if budget_giornaliero >= 20 else "ABO (Budget a livello Gruppo per test controllato)",
                "budget_giornaliero_eur": str(budget_giornaliero.quantize(Decimal("0.01"))),
                "durata_giorni": giorni,
                "budget_totale_eur": str(totale),
            },
            "livello_gruppo_inserzioni": {
                "evento_conversione": obj_info["conversion_event"],
                "ottimizzazione_consegna": obj_info["optimization_goal"],
                "ripartizione_consigliata_eur_giorno": {
                    "gruppo_principale_70pct": str(budget_core),
                    "gruppo_test_creativita_30pct": str(budget_test),
                },
                "posizionamenti": "Advantage+ oppure manuale (Feed 4:5 + Stories/Reels 9:16)",
            },
            "avviso_critico": obj_info["warning"],
        },
        "utm_pronti": {
            "angolo_1_problema": build_utm_url(url, slug, "angolo_1_problema"),
            "angolo_2_risultato": build_utm_url(url, slug, "angolo_2_risultato"),
            "angolo_3_offerta": build_utm_url(url, slug, "angolo_3_offerta"),
        },
        "formati_visual": CREATIVE_SPECS,
        "piattaforma_sito": piattaforma_sito,
        "checklist_sito": SITE_CHECKLIST[piattaforma_sito],
    }


def format_text(plan: dict) -> str:
    setup = plan["meta_ads_setup"]
    camp = setup["livello_campagna"]
    grp = setup["livello_gruppo_inserzioni"]
    lines = [
        f"=== PIANO META ADS: {plan['campagna']} ===",
        f"Obiettivo Meta: {camp['obiettivo']}",
        f"Strategia Budget: {camp['strategia_budget']}",
        f"Budget: {camp['budget_giornaliero_eur']} EUR/giorno x {camp['durata_giorni']} giorni = {camp['budget_totale_eur']} EUR totali",
        f"Split Test: Principale {grp['ripartizione_consigliata_eur_giorno']['gruppo_principale_70pct']} EUR/g | Test {grp['ripartizione_consigliata_eur_giorno']['gruppo_test_creativita_30pct']} EUR/g",
        f"Evento / Ottimizzazione: {grp['evento_conversione']} -> {grp['ottimizzazione_consegna']}",
        f"ATTENZIONE: {setup['avviso_critico']}",
        "",
        "--- URL CON UTM PRONTI ---",
    ]
    for k, v in plan["utm_pronti"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("--- FORMATI VISUAL DA ESPORTARE ---")
    for spec in plan["formati_visual"]:
        lines.append(f"- {spec['formato']} [{spec['ratio']} | {spec['pixel']}]: {spec['note']}")
    lines.append("")
    lines.append(f"--- CHECKLIST SITO ({plan['piattaforma_sito'].upper()}) ---")
    for idx, item in enumerate(plan["checklist_sito"], 1):
        lines.append(f"{idx}. [ ] {item}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera piano campagna Meta Ads, UTM e checklist sito.")
    parser.add_argument("--nome", required=True, help="Nome campagna")
    parser.add_argument("--obiettivo", required=True, choices=list(OBJECTIVE_MAP.keys()))
    parser.add_argument("--budget-giornaliero", required=True, type=Decimal)
    parser.add_argument("--giorni", type=int, default=14)
    parser.add_argument("--url", required=True, help="URL landing page di destinazione")
    parser.add_argument("--piattaforma-sito", default="lovable", choices=list(SITE_CHECKLIST.keys()))
    parser.add_argument("--format", default="text", choices=["text", "json"])
    args = parser.parse_args()

    plan = build_plan(
        nome=args.nome,
        obiettivo=args.obiettivo,
        budget_giornaliero=args.budget_giornaliero,
        giorni=args.giorni,
        url=args.url,
        piattaforma_sito=args.piattaforma_sito,
    )
    if args.format == "json":
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(format_text(plan))


if __name__ == "__main__":
    main()
