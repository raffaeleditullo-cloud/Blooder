# BLOODER — Master Plan & Note di Regia

> **Scopo di questo file:** Mappa strategica viva del progetto **Blooder**. Qui teniamo traccia dell'arsenale selezionato (*Libreria skill* e *Strumenti*), dei motivi per cui teniamo o scartiamo ciò che troviamo sui Reel/GitHub, e di **come combineremo questi mattoni** quando decideremo la piattaforma finale da costruire.

---

## 1. Architettura e Regole Fisse di Blooder

- **Avvio rapido:** doppio click su `avvia_blooder.bat` (`http://127.0.0.1:8765`).
- **Salvataggio rapido:** doppio click su `salva_progetto.bat` (verifica integrità DB SQLite, aggiorna `backup_libreria.json` in chiaro e salva uno snapshot Git locale).
- **Base grafica unica ("Red Matrix"):** definita in `static/` (`index.html`, `styles.css`, `app.js`, `fx.js`, `logo.svg`, font locali `Barlow` / `Barlow Condensed`). Non va mai rigenerata da zero né alterata con colori fuori tema o stili `style=""` inline.
- **Due sezioni distinte nella barra laterale:**
  1. **Libreria skill (`kind = 'skill'`):** Skill per agenti AI, framework e moduli integrabili per costruire/migliorare piattaforme.
  2. **Strumenti (`kind = 'tool'`):** Programmi standalone e utility CLI di sistema che gli agenti possono comandare dall'esterno.

---

## 2. Arsenale Attuale e Come Useremo Ogni Pezzo

### A. Reparto Raccolta Dati & Connettori (I "Sensi")
1. **Agent-Reach** (`Panniantong/agent-reach`) — *Skill*
   - **Come la useremo:** Per dare alla futura piattaforma accesso gratuito a discussioni reali su Reddit, X/Twitter, trascrizioni YouTube, GitHub e forum senza pagare abbonamenti API mensili.
2. **Reverse API Engineer** (`kalil0321/reverse-api-engineer`) — *Skill*
   - **Come la useremo:** Quando la nostra piattaforma dovrà leggere dati strutturati da portali web che non offrono API pubbliche ufficiali, catturando il traffico browser (HAR) e generando connettori Python/TypeScript puliti.

### B. Reparto Sistema Operativo & Mobile (Le "Mani")
3. **Agent Desktop** (`vercel-labs/agent-desktop`) — *Strumento*
   - **Come lo useremo:** Per automatizzare programmi installati su PC (Windows/Mac/Linux) — anche vecchi gestionali senza web e senza API — leggendo direttamente pulsanti e campi dal sistema operativo, senza muovere il mouse e senza sprecare token in screenshot.
4. **xtool** (`xtool-org/xtool`) — *Skill*
   - **Come la useremo:** Se vorremo affiancare alla piattaforma web una vera **app nativa iPhone (`.ipa` in Swift)** compilata, firmata e testata direttamente dal tuo PC Windows (via WSL2), senza dover comprare un Mac.

### C. Reparto Motore AI & Sicurezza (Cervello e Scudo)
5. **Ruflo** (`ruvnet/ruflo`) — *Skill*
   - **Come la useremo:** Solo se la piattaforma finale richiederà più agenti AI che lavorano in parallelo sullo stesso compito complesso mantenendo una memoria condivisa.
6. **PentAGI** (`vxcontrol/pentagi`) — *Skill*
   - **Come la useremo:** **Prima di pubblicare online la piattaforma finale**, la faremo attaccare in privato dentro una stanza Docker isolata da PentAGI per scovare e chiudere porte lasciate aperte su login, API e database.

### D. Reparto Fiducia, Lancio & Guide Utente (Il Ponte verso le Persone)
7. **Marketing Psychology** (`coreyhaines31/marketingskills`) — *Skill*
   - **Come la useremo:** Per superare lo scoglio più duro (*far fidare gli utenti senza budget pubblicitario*). La useremo per scrivere e revisionare landing page, struttura prezzi, SEO e testi usando oltre 70 modelli psicologici di conversione.
8. **Teach** (`mattpocock/skills`) — *Skill*
   - **Come la useremo:** In una cartella dedicata (`/guides`), la useremo per far generare all'agente **mini-lezioni HTML interattive (`lessons/*.html`) e schede pratiche riassuntive (`reference/*.html`)** che spiegano agli utenti come usare la nostra piattaforma passo dopo passo, con estrema semplicità.
9. **Anatomy** (`wheresryan22/anatomy`) — *Skill*
   - **Come la useremo:** In coppia con **Teach** e **Marketing Psychology**! Genera disegni tecnici interattivi e animati (SVG isometrici / WebGL stile *Linear*) da inserire dentro le guide utente e nella home page per far "toccare con mano" visivamente come funziona la piattaforma.

---

## 3. Criteri di Filtro per i Prossimi Reel / Link (Anti-Doppioni)

Per mantenere l'arsenale pulito ed evitare confusione, **scartiamo** ciò che duplica cose che abbiamo già:
- *Già scartate / ridondanti:*
  - `Last 30 Days` (`mvanhorn/last30days-skill`) → tenuta fuori perché coperta in modo più ampio da **Agent-Reach**.
  - `Chief of Staff` (`mattpocock/skills`) → coperta sul fronte multi-agente da **Ruflo** (ed è comunque già inclusa nello stesso repo di `Teach` se mai servisse).

### Cosa potrebbe ancora arricchirci se capita nei prossimi Reel:
- **UI / Design System rapidi o componenti animati web** ad altissima resa visiva;
- **Pagamenti / Autenticazione zero-costi** (soluzioni open-source pronte per gestire utenti, abbonamenti o licenze senza commissioni pesanti);
- **Voce / Video / Estrazione Documenti (OCR/PDF)** gratuiti in locale;
- **Database / Memoria locale veloce** o deploy gratuito in 1 click.

---

## 4. Sinergie Pronte (Note per quando sceglieremo cosa costruire)

- **Combo "Lancio Perfetto senza Budget":** `Marketing Psychology` (testi + leve di fiducia) + `Anatomy` (illustrazioni interattive sulla pagina) + `Teach` (centro guide intuitivo per chi entra la prima volta).
- **Combo "Automazione Totale Web + PC":** `Agent-Reach` (legge social/web) + `Reverse API Engineer` (estrae API dai siti) + `Agent Desktop` (inserisce o legge dati nei programmi desktop sul PC).
- **Combo "Prodotto Blindato Web + iPhone da Windows":** Sviluppo piattaforma → audit sicurezza con `PentAGI` → app iOS nativa firmata da Windows con `xtool`.
