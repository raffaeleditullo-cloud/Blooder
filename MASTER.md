# BLOODER — Master Plan & Note di Regia

> **Scopo di questo file:** Mappa strategica viva del progetto **Blooder**. Qui teniamo traccia dell'arsenale selezionato (*Libreria skill* e *Strumenti*), dei motivi per cui teniamo o scartiamo ciò che troviamo sui Reel/GitHub, e di **come combineremo questi mattoni** quando decideremo la piattaforma finale da costruire.

---

## 1. Architettura e Regole Fisse di Blooder

- **Avvio rapido:** doppio click su `avvia_blooder.bat` (`http://127.0.0.1:8765`).
- **Salvataggio e pubblicazione rapida:** doppio click su `salva_progetto.bat` (esegue `sync_libreria.py`: verifica integrità DB SQLite, scansiona i file contro chiavi/segreti, esporta `backup_libreria.json`, genera il `README.md` vetrina con loghi e tabelle, esporta le Blooderskills in `skills/<nome>/SKILL.md` e sincronizza su GitHub `raffaeleditullo-cloud/Blooder`).
- **Base grafica unica ("Red Matrix"):** definita in `static/` (`index.html`, `styles.css`, `app.js`, `fx.js`, `logo.svg`, `logo-full.svg`, `hero-banner.svg`, font locali `Barlow` / `Barlow Condensed`). Non va mai rigenerata da zero né alterata con colori fuori tema o stili `style=""` inline.
- **Tre sezioni distinte nella barra laterale:**
  1. **Libreria skill (`kind = 'skill'`):** Skill per agenti AI, framework e moduli integrabili selezionati dall'ecosistema open-source.
  2. **Strumenti (`kind = 'tool'`):** Programmi standalone e utility CLI di sistema che gli agenti possono comandare dall'esterno.
  3. **Blooderskills (tabella `blooderskills` + cartella `skills/`):** Le nostre skill originali verticali per settore piattaforma (*"il pezzo in più al muratore"*), testate in chat e installabili a nostro nome con `npx skills add raffaeleditullo-cloud/Blooder --skill <nome>`.

---

## 2. Arsenale Attuale e Come Useremo Ogni Pezzo

### A. Reparto Raccolta Dati & Connettori (I "Sensi")
1. **Agent-Reach** (`Panniantong/agent-reach`) — *Skill*
   - **Come la useremo:** Per dare alla futura piattaforma accesso gratuito a discussioni reali su Reddit, X/Twitter, trascrizioni YouTube, GitHub e forum senza pagare abbonamenti API mensili.
2. **Reverse API Engineer** (`kalil0321/reverse-api-engineer`) — *Skill*
   - **Come la useremo:** Quando la nostra piattaforma dovrà leggere dati strutturati da portali web che non offrono API pubbliche ufficiali, catturando il traffico browser (HAR) e generando connettori Python/TypeScript puliti.

### B. Reparto Sistema Operativo, Desktop & Mobile (Le "Mani")
3. **Agent Desktop** (`vercel-labs/agent-desktop`) — *Strumento*
   - **Come lo useremo:** Per automatizzare programmi installati su PC (Windows/Mac/Linux) — anche vecchi gestionali senza web e senza API — leggendo direttamente pulsanti e campi dal sistema operativo, senza muovere il mouse e senza sprecare token in screenshot.
4. **xtool** (`xtool-org/xtool`) — *Skill*
   - **Come la useremo:** Se vorremo affiancare alla piattaforma web una vera **app nativa iPhone (`.ipa` in Swift)** compilata, firmata e testata direttamente dal tuo PC Windows (via WSL2), senza dover comprare un Mac.
5. **Rune** (`anomalyco/rune`) — *Skill*
   - **Come la useremo:** Quando vorremo distribuire un nostro software come **vero programma Desktop nativo (`.exe` su Windows, Mac e Linux)** leggerissimo e renderizzato su GPU (senza Electron e senza obbligare il cliente a installare Python), facendo sì che l'agente AI costruisca, fotografi (`--snap`), legga l'albero UI (`--tree`) e testi la finestra da solo in modalità headless.

### C. Reparto Motore AI, Disciplina Codice & Sicurezza (Cervello, Briglie e Scudo)
6. **Andrej Karpathy Skills** (`multica-ai/andrej-karpathy-skills`) — *Skill*
   - **Come la useremo:** Come regola fissa nella cartella di ogni progetto che costruiremo per obbligare l'agente AI a rispettare le 4 regole d'oro: chiedere invece di tirare a indovinare, scrivere il minimo codice indispensabile, fare modifiche chirurgiche senza toccare file vicini e verificare tutto prima di dire "fatto".
7. **Ruflo** (`ruvnet/ruflo`) — *Skill*
   - **Come la useremo:** Solo se la piattaforma finale richiederà più agenti AI che lavorano in parallelo sullo stesso compito complesso mantenendo una memoria condivisa.
8. **PentAGI** (`vxcontrol/pentagi`) — *Skill*
   - **Come la useremo:** **Prima di pubblicare online la piattaforma finale**, la faremo attaccare in privato dentro una stanza Docker isolata da PentAGI per scovare e chiudere porte lasciate aperte su login, API e database.

### D. Reparto Validazione Business, Fiducia & Guide Utente (Strategia e Ponte verso le Persone)
9. **Founder** (`Jakeschincariol/founder-skill`) — *Skill*
   - **Come la useremo:** **Prima ancora di iniziare a programmare** una piattaforma! La useremo per far giudicare l'idea dal CFO virtuale (calcolo margini netti reali e prezzi sostenibili) e da **100 clienti simulati** con budget e obiezioni diverse, così scartiamo subito le idee in perdita e partiamo solo su ciò che sta in piedi economicamente.
10. **Marketing Psychology** (`coreyhaines31/marketingskills`) — *Skill*
    - **Come la useremo:** Per superare lo scoglio più duro (*far fidare gli utenti senza budget pubblicitario*). La useremo per scrivere e revisionare landing page, struttura prezzi, SEO e testi usando oltre 70 modelli psicologici di conversione.
11. **Sepia** (`Nanako0129/sepia`) — *Skill*
    - **Come la useremo:** In coppia fissa con **Marketing Psychology**! Basata sullo studio *StoryScope* di Google DeepMind e Università del Maryland, ripulisce la struttura profonda di email, landing page, post e comunicazioni eliminando ogni traccia di "testo scritto da un robot" (niente elenchi scontati né frasi astratte, solo prosa concreta e umana).
12. **Teach** (`mattpocock/skills`) — *Skill*
    - **Come la useremo:** In una cartella dedicata (`/guides`), la useremo per far generare all'agente **mini-lezioni HTML interattive (`lessons/*.html`) e schede pratiche riassuntive (`reference/*.html`)** che spiegano agli utenti come usare la nostra piattaforma passo dopo passo, con estrema semplicità.
13. **Anatomy** (`wheresryan22/anatomy`) — *Skill*
    - **Come la useremo:** In coppia con **Teach** e **Marketing Psychology**! Genera disegni tecnici interattivi e animati (SVG isometrici / WebGL stile *Linear*) da inserire dentro le guide utente e nella home page per far "toccare con mano" visivamente come funziona la piattaforma.

---

## 3. Criteri di Filtro per i Prossimi Reel / Link (Anti-Doppioni)

Per mantenere l'arsenale pulito ed evitare confusione, **scartiamo** ciò che duplica cose che abbiamo già o non gira sul nostro sistema:
- *Già scartate / ridondanti:*
  - `Last 30 Days` (`mvanhorn/last30days-skill`) → tenuta fuori perché coperta in modo più ampio da **Agent-Reach**.
  - `Chief of Staff` (`mattpocock/skills`) → coperta sul fronte multi-agente da **Ruflo** (ed è comunque già inclusa nello stesso repo di `Teach` se mai servisse).
  - `Atticus` (`SaarthurR/atticus-mac`) → scartato perché funziona solo ed esclusivamente su Mac (macOS) e sul fronte controllo PC è già superato dal nostro **Agent Desktop** multipiattaforma (Windows/Mac/Linux).
  - `4 Prompt ASD-STE100` (Karpathy prompts) → scartati come scheda perché sono semplici prompt testuali da chat e tutte le loro funzioni sono già coperte in modo nettamente superiore da **Teach** (pagine HTML didattiche), **Anatomy** (schemi interattivi) e **Sepia** (scrittura pulita e umana).

### Cosa potrebbe ancora arricchirci se capita nei prossimi Reel:
- **UI / Design System rapidi o componenti animati web** ad altissima resa visiva;
- **Pagamenti / Autenticazione zero-costi** (soluzioni open-source pronte per gestire utenti, abbonamenti o licenze senza commissioni pesanti);
- **Voce / Video / Estrazione Documenti (OCR/PDF)** gratuiti in locale su Windows;
- **Database / Memoria locale veloce** o deploy gratuito in 1 click.

---

## 4. Sinergie Pronte (Note per quando sceglieremo cosa costruire)

- **Combo "Prova Generale a Rischio Zero":** `Agent-Reach` (ascolta problemi veri su Reddit/forum) + `Founder` (calcola margini reali col CFO e testa l'offerta su 100 clienti simulati prima di scrivere una riga di codice).
- **Combo "Lancio Perfetto senza Budget":** `Marketing Psychology` (leve psicologiche di fiducia) + `Sepia` (toglie ogni tono artificiale dai testi) + `Anatomy` (illustrazioni interattive sulla pagina) + `Teach` (centro guide intuitivo per chi entra la prima volta).
- **Combo "Automazione Totale Web + PC":** `Agent-Reach` (legge social/web) + `Reverse API Engineer` (estrae API dai siti) + `Agent Desktop` (inserisce o legge dati nei programmi desktop sul PC).
- **Combo "Prodotto Blindato e Pulito":** Sviluppo disciplinato con `Andrej Karpathy Skills` → audit sicurezza con `PentAGI` → rilascio Desktop nativo con `Rune` o app iOS da Windows con `xtool`.

---

## 5. Stato del Progetto & Prossimi Passi

- **Repository GitHub collegato e allineato (`main`):** `https://github.com/raffaeleditullo-cloud/Blooder` (Licenza MIT, vetrina `README.md` auto-generata con loghi Red Matrix e controllo automatico anti-chiavi attivo in `sync_libreria.py`).
- **Prima Blooderskill pubblicata e collaudata (`skills/fatturapa-xray/`):**
  - **`FatturaPA X-Ray`** — motore deterministico Python zero-dipendenze (`scripts/xray_fatture.py`) + guida operativa fiscale italiana (`SKILL.md`) per aprire buste `.xml` e `.xml.p7m`, sottrarre note di credito `TD04`, escludere doppioni, scovare rincari silenziosi dei fornitori, bloccare scarti SdI/bollo e calcolare il netto reale (Forfettario e Ordinario).
- **Prossimo passo concordato:**
  1. Costruire il **Laboratorio Visivo & Simulatore Interattivo** (`static/labs/fatturapa-xray.html` collegato con pulsante nella scheda Blooderskill, unendo i principi di **Teach** + **Anatomy** in stile *Red Matrix*) per far capire e simulare dal vivo ogni Blooderskill anche a chi parte da zero;
  2. Proseguire con nuove Blooderskills verticali e selezione di skill/strumenti open-source.
