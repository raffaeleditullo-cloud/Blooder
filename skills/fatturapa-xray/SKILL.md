---
name: fatturapa-xray
description: "Analisi deterministica, controllo anti-scarto SdI, rilevamento rincari fornitori e calcolo netto reale (Forfettario e Ordinario) su Fatture Elettroniche Italiane (.xml e .xml.p7m). Usa questa skill ogni volta che devi leggere cartelle di fatture elettroniche italiane, scovare aumenti di prezzo nascosti, validare tracciati FatturaPA v1.2.2 (FPR12/FPA12) o programmare funzioni per software di fatturazione in Italia."
---

# FatturaPA X-Ray — Intelligenza Fiscale & Anti-Scarto SdI (Italia)

> **Modulo Originale Blooderskill** | Zero dipendenze esterne (Python 3.10+ standard library) | 100% esecuzione locale offline per massima privacy fiscale.

## Quando attivare questa skill
Attiva sempre **FatturaPA X-Ray** in due scenari:
1. **Analisi operativa in chat (Imprenditori, Artigiani, Consulenti, P.IVA):** l'utente fornisce un file o una cartella di fatture elettroniche `.xml` o `.xml.p7m` (scaricate da Cassetto Fiscale AdE, Aruba, Fatture in Cloud, TeamSystem, ecc.) e vuole sapere rincari fornitori, doppioni, canoni ricorrenti, errori SdI o quanto gli resta davvero netto in tasca.
2. **Sviluppo software di fatturazione / gestionali italiani:** stai scrivendo codice backend/frontend che genera, importa o valida tracciati `FatturaPA` (`FPR12` / `FPA12`) e devi evitare errori tipici dei modelli AI generalisti (che non conoscono le regole dell'Agenzia delle Entrate).

---

## 1. Uso del Motore Deterministico (`scripts/xray_fatture.py`)

Non sommare mai a mente né stimare importi XML con calcoli approssimativi: esegui **sempre** lo script incluso nella skill (`Decimal` al centesimo con arrotondamento fiscale `ROUND_HALF_UP`):

```bash
# Caso Forfettario (preset ATECO: artigiani=86%, professionisti=78%, software=67%, commercio=40%)
python <percorso-skill>/scripts/xray_fatture.py "<cartella-fatture>" --piva <PIVA_UTENTE> --regime forfettario --ateco artigiani

# Caso Forfettario Start-up (imposta sostitutiva 5%) con coefficiente personalizzato
python <percorso-skill>/scripts/xray_fatture.py "<cartella-fatture>" --piva <PIVA_UTENTE> --regime forfettario --coeff 78 --imposta-pct 5

# Caso Regime Ordinario / Semplificato (scorporo IVA a debito vs IVA a credito detraibile)
python <percorso-skill>/scripts/xray_fatture.py "<cartella-fatture>" --piva <PIVA_UTENTE> --regime ordinario

# Output JSON strutturato (per generare dashboard HTML interattive o alimentare altre skill come Anatomy)
python <percorso-skill>/scripts/xray_fatture.py "<cartella-fatture>" --format json
```

### Cosa gestisce in automatico lo script
- **Sbucciatura `.xml.p7m` nativa:** apre sia buste binarie `ASN.1 DER/BER` (anche con *chunked OCTET STRING*) sia buste `.p7m` codificate in `Base64`/`PEM`, oltre a XML con BOM o encoding `Windows-1252`/`ISO-8859-1`, ignorando le ricevute di notifica SdI (`_RC_`, `_NS_`, `_MC_`, `_DT_`).
- **Deduzione automatica P.IVA titolare:** se `--piva` non viene passato, individua la Partita IVA ricorrente e separa **Fatture Emesse (Attive)** da **Fatture Ricevute (Passive)**.
- **Esclusione automatica doppioni:** se la stessa fattura (es. `.xml` e `.xml.p7m` con identico fornitore e numero documento) compare due volte nella cartella, la segnala come doppione e la **esclude dai totali economici** evitando doppi conteggi.

---

## 2. Le 7 Regole d'Oro della FatturaPA Italiana (Invarianti per Codice & Analisi)

Quando scrivi codice per gestionali italiani o interpreti i risultati per l'utente, applica tassativamente queste regole:

1. **Segno algebrico Note di Credito (`TD04` e `TD08`):**
   - Nel tracciato XML gli importi di una Nota di Credito sono scritti con numeri positivi, ma contabilmente e fiscalmente **vanno SEMPRE sottratti (`segno = -1`)** dal fatturato o dai costi, e **non vanno usati** come variazioni di listino nello storico rincari fornitori.
2. **Sottocodici `<Natura>` obbligatori (Errore SdI `00445`):**
   - I vecchi codici padre generici **`N2`, `N3`, `N6` sono aboliti e causano scarto immediato SdI**. Usa esclusivamente i sottocodici specifici:
     - `N2.1` (non soggette art. 7-7septies) | `N2.2` (non soggette altri casi — **obbligatorio per Regime Forfettario RF19**);
     - `N3.1`..`N3.6` (non imponibili esportazioni/cessioni intra-UE);
     - `N6.1`..`N6.9` (inversione contabile / *reverse charge* edilizia, subappalti, elettronica).
3. **Mutua esclusione `AliquotaIVA` e `Natura` (`00400` / `00401`):**
   - Se `AliquotaIVA == 0.00`, `<Natura>` è obbligatoria (`00400`). Se `AliquotaIVA > 0.00`, `<Natura>` **non** deve esistere (`00401`).
4. **Marca da Bollo Virtuale da `2,00 €` sopra `77,47 €` (`DM 17/06/2014`):**
   - Obbligatoria (`<BolloVirtuale>SI</BolloVirtuale>`) quando la somma delle righe con natura `N2.1`, `N2.2`, `N3.5`, `N3.6` o `N4` supera **`77,47 €`**. Se il bollo viene riaddebitato in fattura al cliente da un contribuente Forfettario, concorre al reddito forfettario (*Risposta AdE n. 428/2022*).
5. **Lunghezza `CodiceDestinatario` (`00311`):**
   - Esattamente **`7` caratteri** per privati B2B/B2C (`FormatoTrasmissione = FPR12`, `0000000` se via PEC o privato senza codice, `XXXXXXX` per estero) ed esattamente **`6` caratteri** per Pubblica Amministrazione (`FPA12`).
6. **Differenza radicale sull'IVA Acquisti tra Forfettario e Ordinario:**
   - **Regime Forfettario:** l'IVA pagata sulle fatture dei fornitori **NON è detraibile** (è un costo vivo al 100%), mentre tasse e INPS si calcolano solo su `Incassato × Coefficiente ATECO` (non scaricando le fatture di acquisto). Pertanto un rincaro del fornitore mangia direttamente euro netti dalla tasca del forfettario!
   - **Regime Ordinario / Semplificato:** l'IVA sugli acquisti inerenti va a credito e riduce l'IVA a debito da versare allo Stato; i costi imponibili riducono l'utile tassabile.
7. **Quadratura al centesimo (`00423` / `00421` / `00422`):**
   - Ogni `DettaglioLinee` deve rispettare `|PrezzoTotale - (Quantita * PrezzoUnitario * FattoreSconto)| <= 0,01 €`, e ogni `DatiRiepilogo` deve coincidere con la somma delle righe aventi pari `(AliquotaIVA, Natura)`.

---

## 3. Formato consigliato di risposta per l'utente
Dopo aver eseguito `scripts/xray_fatture.py`, presenta sempre i risultati in italiano semplice e diretto seguendo questa scaletta:
1. **Verdetto Tasca (Salvadanaio & Netto Vero):** quanti soldi entrano davvero, quanti vanno messi subito da parte per Stato/INPS e quanto resta pulito.
2. **Allarme Rincari Fornitori:** tabella chiara con nome fornitore, articolo, vecchio prezzo, nuovo prezzo, `%` di aumento ed euro persi (suggerendo di rinegoziare o aggiornare il proprio listino di vendita).
3. **Scudo Anti-Scarto / Doppioni:** eventuali bozze che verrebbero rifiutate dallo SdI, bolli mancanti, fatture doppie o canoni mensili dimenticati.
