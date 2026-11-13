---
name: blooder-regia
description: >-
  Protocollo decisionale obbligatorio di Blooder per selezionare, leggere e applicare
  le skill della libreria (Founder, Karpathy, Understand Anything, Sepia, Marketing Psychology,
  Teach, Anatomy, Strix, Claude Video, Agent-Reach, Reverse API Engineer e tutte le Blooderskills)
  prima di prendere qualsiasi decisione, valutare nuovi link/Reel, scrivere codice o progettare piattaforme.
---

# Blooder Regia — Motore Decisionale basato sulle Skill

> **Principio cardine:** La libreria di Blooder non è uno scaffale passivo. Ogni decisione tecnica, economica, editoriale o di selezione tool **deve** passare attraverso le skill montate in `.agents/vendor_skills/` e `skills/`.

## Procedura Obbligatoria Prima di Decidere o Agire

1. **Identifica il tipo di decisione** usando la matrice qui sotto.
2. **Apri e leggi il `SKILL.md` corrispondente** (in `.agents/vendor_skills/<nome>/SKILL.md` o `skills/<nome>/SKILL.md`) prima di formulare il verdetto o scrivere codice.
3. **Esegui gli script deterministici della skill** quando sono presenti (es. `unit_economics.py` per i margini in `founder-cfo`, `panel.py` per il test acquirenti in `founder-consumer`, `xray_fatture.py` in `fatturapa-xray`).
4. **Dichiara sempre nella risposta** quali skill di Blooder hai applicato per arrivare a quella conclusione (es. *`Skill usate: karpathy-guidelines + sepia`*).

## Matrice di Attivazione Skill

| Situazione / Decisione | Skill da leggere e applicare | Cosa controlla in concreto |
| :--- | :--- | :--- |
| **Valutazione di nuovi Reel / repository GitHub** | `karpathy-guidelines` + `founder-board` + controllo `blooder.db` | Niente hype: verifica codice reale su GitHub, licenza, supporto Windows, costi nascosti (token/API) e **filtro anti-doppioni** (sostituisce una skill esistente solo se è nettamente superiore). |
| **Scelta o validazione di una piattaforma / idea di business o listino** | `founder-board` + `founder-cfo` + `founder-pricing` + `founder-consumer` | Margini netti reali (`unit_economics.py`), sostenibilità prezzi e obiezioni su 100 clienti simulati prima di scrivere codice. |
| **Modifiche a codice, database o progetti esistenti** | `karpathy-guidelines` + `understand-diff` | Minimo codice indispensabile, zero modifiche fuori bersaglio e analisi preventiva delle dipendenze (`Diff Impact`) per non rompere nulla altrove. |
| **Scrittura di testi, schede libreria, report, `MASTER.md` o risposte lunghe** | `sepia` | Architettura logica concreta (*StoryScope*), zero frasi fatte da chatbot, limiti reali scritti con onestà in `honest_tradeoffs`. |
| **Landing page, posizionamento, conversioni e fiducia utenti** | `marketing-psychology` + `cro` + `sepia` | Oltre 70 modelli psicologici reali uniti a prosa umana credibile. |
| **Creazione di guide utente o Laboratori Visivi (`static/labs/*.html`)** | `teach` + `anatomy` | Spiegazioni un passo alla volta con schemi interattivi funzionanti, rispettando sempre la palette *Red Matrix* di Blooder. |
| **Controllo sicurezza del codice prima di pubblicare** | `find-security-vulnerabilities-in-code` (*Strix*) | Ricerca vulnerabilità reali (`SQLi`, `XSS`, `SSRF`, segreti, permessi) e scrittura immediata delle patch. |
| **Analisi di video/tutorial o estrazione API / dati web** | `watch` (*Claude Video*) / `agent-reach` / `reverse-api-engineer` | Estrazione frame + parlato da video, ricerca web gratuita o generazione connettori API puliti. |
| **Analisi e quadratura Fatture Elettroniche XML** | `fatturapa-xray` (`skills/fatturapa-xray/`) | Calcolo al centesimo algebrico tramite `scripts/xray_fatture.py`. |

## Se `.agents/vendor_skills/` è vuota (Nuovo PC)
Lancia subito:
```powershell
python attiva_arsenale.py
```
per scaricare e montare in locale tutte le skill operative della libreria Blooder.
