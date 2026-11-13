---
name: service-as-software-it
description: "Applica il modello Sequoia Capital ('I servizi sono il nuovo software') alla realtà fiscale e alle PMI italiane: confronta al centesimo con script Python deterministico la vendita di un abbonamento SaaS fai-da-te contro la vendita di un Servizio Finito Chiavi in Mano erogato internamente con l'AI (calcolando Forfettario 5%/15% + INPS, Ordinario, tetto 85.000€, abbandono clienti e guadagno netto orario reale). Usa sempre questa skill quando valuti come monetizzare un'idea, un flusso AI o una piattaforma per aziende italiane."
---

# Service-as-a-Software Italia — Motore Sequoia & Netto Reale

> **Modulo Originale Blooderskill** | Potenzia: `Founder` (`founder-board`, `founder-cfo`, `founder-offer`, `founder-pricing`), `Sepia` | Zero dipendenze esterne (Python 3.10+ `Decimal`).

## Il Pezzo in Più (Perché in Italia il "Servizio AI" batte il SaaS 9 volte su 10)
Secondo l'analisi di **Sequoia Capital**, per ogni `1 €` speso dalle aziende in software, `6 €` vengono spesi in servizi finiti. In Italia questo divario è ancora più forte: l'artigiano, l'agenzia, lo studio o la PMI **non vuole pagare 39€/mese per studiare l'ennesimo pannello software**, ma paga subito **300€–1.200€/mese** chi gli toglie il problema consegnandogli il risultato già pronto e verificato.
Inoltre il modulo americano `founder-cfo` ignora una trappola cruciale italiana: nel **Regime Forfettario** le spese API/server **non si scaricano dalle tasse** (escono dritte dal netto!), esiste il tetto rigido di **`85.000 €/anno`** (`7.083 €/mese`) e i contributi INPS incidono in modo diretto.

---

## 1. Esecuzione Obbligatoria dello Script (`scripts/confronta_saas_servizio.py`)

Non stimare mai a occhio se conviene vendere un abbonamento software o il servizio chiavi in mano. Lancia sempre il calcolatore deterministico incluso:

```bash
# Confronto standard per arrivare a 3.000 € netti puliti in tasca al mese in Forfettario start-up (5%)
python skills/service-as-software-it/scripts/confronta_saas_servizio.py --target-netto 3000 --saas-prezzo 39 --servizio-prezzo 390 --minuti-manuali-prima 240 --minuti-umani-con-ai 25 --regime forfettario --ateco servizi_imprese --imposta-forf-pct 5

# Confronto in Forfettario standard (15%) o Regime Ordinario / SRL
python skills/service-as-software-it/scripts/confronta_saas_servizio.py --target-netto 5000 --saas-prezzo 49 --servizio-prezzo 600 --regime ordinario

# Output JSON strutturato per report o dashboard
python skills/service-as-software-it/scripts/confronta_saas_servizio.py --target-netto 3000 --format json
```

---

## 2. Il Protocollo in 4 Mosse per Costruire un'Offerta "Service-as-a-Software"
Quando un progetto mostra nello script un vantaggio netto del **Modello B (Servizio Finito)** rispetto al SaaS fai-da-te:
1. **Individua un lavoro ripetitivo pagato a caro prezzo oggi fatto a mano** (es. controllo fatture/listini fornitori, preparazione pratiche/preventivi tecnici, pulizia cataloghi, audit siti/campagne, report mensili per clienti).
2. **Nascondi la complessità dietro le quinte:** il cliente non vede prompt, modelli né configurazioni; ti invia i file grezzi (via email, cartella condivisa o un modulo con 1 solo pulsante) e riceve il lavoro finito.
3. **Usa Blooder come "Fabbrica Interna" (90% AI + 10% Regia Umana):** gli script deterministici e gli agenti fanno il lavoro pesante in 2 minuti; tu fai 15–20 minuti di controllo qualità umano garantendo **zero allucinazioni**.
4. ** Prezza sul risultato, mai sulle ore impiegate (`founder-offer`):** se al cliente risparmi 8 ore di studio/impiegato o gli fai recuperare 1.000€ di errori, il servizio vale `350€–800€/mese` anche se a te col motore AI richiede 20 minuti.
