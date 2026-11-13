# Regole Operative di Progetto — BLOODER

Queste regole sono **sempre attive** in questo workspace. La libreria di Blooder esiste per essere **usata davvero in ogni decisione**, mai lasciata ferma come un catalogo passivo.

## 1. Obbligo di Decisione Guidata dalle Skill
Prima di prendere una decisione tecnica o strategica, giudicare nuovi link/Reel, proporre un'idea di piattaforma, scrivere testi importanti o modificare codice:
1. **Seleziona la skill giusta** dall'arsenale attivo (`.agents/skills/blooder-regia/SKILL.md`, `skills/<nome>/SKILL.md` e `.agents/vendor_skills/<nome>/SKILL.md`).
2. **Leggi il `SKILL.md` della skill scelta** (e usa i suoi script Python quando applicabile, come `unit_economics.py`, `panel.py` o `xray_fatture.py`) *prima* di decidere o eseguire.
3. **Trasparenza esplicita:** indica sempre brevemente nella risposta quali skill della libreria Blooder hai applicato per prendere la decisione (es. `Skill applicate: karpathy-guidelines, founder-board, sepia`).

### Mappa Rapida Skill Attive
- **Regia & Filtro Anti-Doppioni Reel/Tool:** `.agents/skills/blooder-regia/SKILL.md`
- **Disciplina Codice & Decisioni Chirurgiche:** `.agents/vendor_skills/karpathy-guidelines/SKILL.md`
- **Impatto Modifiche & Architettura Codice:** `.agents/vendor_skills/understand-diff/SKILL.md` e `understand/SKILL.md`
- **Validazione Economica, Prezzi & Mercato:** `.agents/vendor_skills/founder-board/SKILL.md`, `founder-cfo/SKILL.md`, `founder-pricing/SKILL.md`, `founder-consumer/SKILL.md`
- **Scrittura Concreta e Naturale (Zero Tono Robot):** `.agents/vendor_skills/sepia/SKILL.md`
- **Psicologia Conversioni & Fiducia Utenti:** `.agents/vendor_skills/marketing-psychology/SKILL.md` e `cro/SKILL.md`
- **Guide Didattiche & Schemi Interattivi:** `.agents/vendor_skills/teach/SKILL.md` e `anatomy/SKILL.md`
- **Sicurezza Codice & Patch Vulnerabilità:** `.agents/vendor_skills/find-security-vulnerabilities-in-code/SKILL.md` (*Strix*)
- **Analisi Video, Ricerca Web & API:** `.agents/vendor_skills/watch/SKILL.md`, `agent-reach/SKILL.md`, `reverse-api-engineer/SKILL.md`
- **Blooderskills Verticali Originali:** `skills/` (es. `skills/fatturapa-xray/SKILL.md`)

*(Se la cartella `.agents/vendor_skills/` non è ancora presente su disco, esegui `python attiva_arsenale.py`).*

## 2. Le 4 Regole Ferree di Karpathy (Sempre Attive)
1. **Pensa prima di agire:** non tirare a indovinare. Se c'è un dubbio reale o due strade con compromessi diversi, esponili chiaramente.
2. **Semplicità assoluta:** scrivi il minimo codice e la struttura più lineare possibile. Niente astrazioni gonfiate, niente doppioni in libreria.
3. **Modifiche chirurgiche:** tocca esclusivamente i file richiesti dal compito. Non alterare codice funzionante vicino.
4. **Verifica concreta:** testa sempre script, integrità DB (`sync_libreria.py`) e risultati reali prima di dichiarare concluso un lavoro.

## 3. Regole Inviolabili di Blooder
- **Design "Red Matrix" bloccato:** non rigenerare né alterare la base grafica in `static/` (`styles.css`, `index.html`, loghi, font `Barlow`), niente colori fuori palette o `style=""` inline improvvisati.
- **Privacy e Sicurezza GitHub (`raffaeleditullo-cloud/Blooder` è pubblico):**
  - Qualsiasi documento con nomi privati, percorsi personali o analisi riservate va salvato **solo** in `_privato/` (protetto da `.gitignore`).
  - Mai inserire chiavi API o segreti nei file tracciati; usa `.\salva_progetto.bat --auto` per eseguire il controllo integrità SQLite e lo scanner anti-chiavi prima del push.
