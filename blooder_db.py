import json
import os
import re
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "blooder.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SEED_SKILLS = [
    {
        "slug": "agent-reach",
        "name": "Agent-Reach",
        "repo_url": "https://github.com/Panniantong/agent-reach",
        "category": "Dati Web & Ricerca",
        "tagline": "Dà ai tuoi agenti AI accesso gratuito a X/Twitter, Reddit, YouTube, GitHub e forum senza pagare API.",
        "simple_explanation": (
            "Normalmente, se la tua app o il tuo agente AI vuole leggere discussioni su Reddit, post su X (Twitter) "
            "o trascrizioni di video YouTube, le piattaforme ti bloccano oppure ti chiedono abbonamenti API costosissimi. "
            "Agent-Reach installa in un colpo solo dei piccoli lettori pubblici e gratuiti così il tuo software può "
            "cercare e leggere informazioni fresche dal web reale a costo zero."
        ),
        "specs": {
            "linguaggio": "Python / CLI",
            "sistemi_operativi": "Windows, macOS, Linux",
            "costo": "100% Gratuito (Open Source)",
            "supporto_mcp": "Sì (nativo)",
            "difficolta": "Facile (1 comando)"
        },
        "compatible_apps": [
            "App di ricerca mercato e analisi trend",
            "Assistenti AI e Chatbot informati in tempo reale",
            "Aggregator di notizie, recensioni o social",
            "Tool SEO e creazione contenuti"
        ],
        "tech_keywords": ["python", "scraping", "search", "api", "twitter", "reddit", "youtube", "mcp", "llm", "agent"],
        "cost_saving": "Evita abbonamenti a X API (da 100$/mese), Reddit API e servizi di scraping a pagamento (30-100€/mese).",
        "honest_tradeoffs": (
            "Non hai le stesse garanzie di velocità e stabilità al 100% di un'API ufficiale pagata: se un social cambia "
            "pagina o mette limiti temporanei, volumi enormi (decine di migliaia di richieste l'ora) possono rallentare. "
            "Perfetto per uso normale, prototipi, agenti e volumi piccoli/medi; meno adatto a sistemi enterprise critici."
        ),
        "install_guide": (
            "1. Assicurati di avere Python 3.10+ installato sul PC.\n"
            "2. Clona o installa il pacchetto dal repository ufficiale:\n"
            "   git clone https://github.com/Panniantong/agent-reach.git\n"
            "3. Esegui la diagnostica rapida per verificare cosa funziona subito sul tuo PC:\n"
            "   agent-reach doctor\n"
            "4. Collegalo come server MCP al tuo agente AI oppure richiamalo via riga di comando dal tuo backend."
        )
    },
    {
        "slug": "reverse-api-engineer",
        "name": "Reverse API Engineer",
        "repo_url": "https://github.com/kalil0321/reverse-api-engineer",
        "category": "Integrazioni & API",
        "tagline": "Osserva il traffico di un sito web nel browser e genera automaticamente il codice pulito per collegarti ai suoi dati.",
        "simple_explanation": (
            "Molti siti web non offrono una documentazione ufficiale per gli sviluppatori, ma dietro le quinte scambiano "
            "dati ordinati col browser. Invece di impazzire a mano negli strumenti per sviluppatori di Chrome, questo tool "
            "registra cosa succede mentre navighi una pagina, scarta la spazzatura pubblicitaria e ti scrive da solo "
            "uno script pronto (in Python, TypeScript, Go, ecc.) per interrogare quei dati."
        ),
        "specs": {
            "linguaggio": "Python (genera codice Python, TS/JS, Go, C#)",
            "sistemi_operativi": "Windows, macOS, Linux",
            "costo": "Gratuito (richiede un modello AI per analizzare il file HAR)",
            "supporto_mcp": "Sì (Skill per agenti coding + Playwright)",
            "difficolta": "Media"
        },
        "compatible_apps": [
            "Comparatori di prezzi, cataloghi e monitoraggio disponibilità",
            "Connettori verso portali aziendali o gestionali vecchi senza API",
            "Automazioni di raccolta dati strutturati",
            "Backend che devono sincronizzarsi con servizi esterni"
        ],
        "tech_keywords": ["api", "sdk", "playwright", "browser", "scraper", "python", "typescript", "fetch", "axios", "har"],
        "cost_saving": "Risparmia giorni di lavoro manuale di reverse-engineering o costosi connettori custom.",
        "honest_tradeoffs": (
            "Il codice generato si basa sulle chiamate interne del sito: se il proprietario del sito aggiorna la struttura "
            "o usa protezioni anti-bot molto pesanti (es. CAPTCHA avanzati o token che scadono ogni 2 minuti), dovrai "
            "rigenerare il client o gestire il rinnovo sessione. Non sostituisce un contratto API ufficiale per usi bancari."
        ),
        "install_guide": (
            "1. Installa il tool tramite pip o uv:\n"
            "   pip install reverse-api-engineer\n"
            "2. Se vuoi guidare tu il browser manualmente, aggiungi Playwright:\n"
            "   pip install \"reverse-api-engineer[manual]\" && playwright install chromium\n"
            "3. Oppure installalo direttamente come skill per il tuo agente coding:\n"
            "   npx skills add kalil0321/reverse-api-engineer"
        )
    },
    {
        "slug": "pentagi",
        "name": "PentAGI",
        "repo_url": "https://github.com/vxcontrol/pentagi",
        "category": "Sicurezza & Audit",
        "tagline": "Squadra autonoma di agenti per testare la sicurezza della tua app in un ambiente Docker isolato.",
        "simple_explanation": (
            "Quando costruisci un sito o un'applicazione (soprattutto velocemente con l'AI), è facilissimo lasciare "
            "porte aperte senza accorgersene. PentAGI avvia una stanza blindata (Docker) con veri strumenti di controllo "
            "sicurezza: tu gli indichi il TUO sito di test, lui cerca falle reali e ti consegna un report chiaro su cosa "
            "chiudere prima di andare online."
        ),
        "specs": {
            "linguaggio": "Go + Interfaccia React",
            "sistemi_operativi": "Windows (con Docker Desktop / WSL2), macOS, Linux",
            "costo": "Gratuito (MIT License - paghi solo il modello AI scelto o usi Ollama gratis)",
            "supporto_mcp": "Interfaccia Web + API GraphQL/REST",
            "difficolta": "Media-Alta (richiede Docker)"
        },
        "compatible_apps": [
            "SaaS e Web App con login utenti e pagamenti",
            "API Backend (Node, Python, Go, PHP) prima della messa online",
            "Piattaforme e-commerce e portali con database clienti",
            "Audit interno di sicurezza pre-rilascio"
        ],
        "tech_keywords": ["security", "auth", "login", "jwt", "sql", "docker", "backend", "saas", "api", "vulnerability"],
        "cost_saving": "Evita scanner di vulnerabilità commerciali da centinaia di euro al mese per i controlli preliminari.",
        "honest_tradeoffs": (
            "Richiede Docker installato (occupa diversi GB di spazio per gli strumenti Kali Linux) e va usato SOLO su "
            "propri progetti o sistemi autorizzati. Non sostituisce al 100% una certificazione legale firmata da un ente "
            "umano se richiesta per legge, ma scova subito gli errori più pericolosi."
        ),
        "install_guide": (
            "1. Installa e avvia Docker Desktop sul tuo PC.\n"
            "2. Scarica il progetto:\n"
            "   git clone https://github.com/vxcontrol/pentagi.git\n"
            "   cd pentagi\n"
            "3. Copia il file .env.example in .env, inserisci la tua chiave LLM (o configura Ollama locale) e avvia:\n"
            "   docker compose up -d\n"
            "4. Usa la modalità 'Assistant' per approvare a mano ogni singolo controllo sulla tua app."
        )
    },
    {
        "slug": "xtool",
        "name": "xtool",
        "repo_url": "https://github.com/xtool-org/xtool",
        "category": "Mobile & iOS",
        "tagline": "Compila, firma e installa vere app iPhone (iOS in Swift) direttamente da Windows o Linux, senza avere un Mac.",
        "simple_explanation": (
            "Di solito Apple ti obbliga a comprare un Mac con Xcode anche solo per compilare e provare una semplice app "
            "sul tuo iPhone. xtool abbatte questo limite: usando Windows (tramite WSL) o Linux, ti permette di trasformare "
            "un progetto Swift in un pacchetto .ipa firmato col tuo account Apple e installarlo via cavo USB sul tuo iPhone."
        ),
        "specs": {
            "linguaggio": "Swift",
            "sistemi_operativi": "Windows (tramite WSL2), Linux, macOS",
            "costo": "100% Gratuito (Open Source)",
            "supporto_mcp": "CLI integrabile da qualsiasi agente coding",
            "difficolta": "Media (serve WSL2 su Windows)"
        },
        "compatible_apps": [
            "App native iOS / iPhone sviluppate da PC Windows o Linux",
            "Companion app mobile per piattaforme Web esistenti",
            "Strumenti personali da installare sul proprio iPhone senza Mac",
            "Pipeline automatiche di build mobile economiche su server Linux"
        ],
        "tech_keywords": ["ios", "iphone", "mobile", "swift", "app", "windows", "linux", "xcode", "ipa"],
        "cost_saving": "Evita l'acquisto obbligatorio di un Mac (800-1.500€) o il noleggio di Mac in cloud per sviluppare e testare su iPhone.",
        "honest_tradeoffs": (
            "Lavora su progetti Swift Package Manager (SwiftPM), non sui vecchi file progetto proprietari di Xcode con "
            "interfaccia grafica drag-and-drop, e non include il simulatore grafico dell'iPhone su schermo PC (testi "
            "direttamente collegando il tuo vero iPhone via USB)."
        ),
        "install_guide": (
            "1. Su Windows attiva WSL2 (Ubuntu) e installa la toolchain Swift + libimobiledevice/usbmuxd.\n"
            "2. Segui la guida ufficiale su https://xtool.sh per importare l'SDK Darwin.\n"
            "3. Collega il tuo iPhone via USB e autentica il tuo Apple ID con `xtool auth`.\n"
            "4. Compila e installa la tua app con `xtool dev` direttamente nella cartella del progetto Swift."
        )
    },
    {
        "slug": "ruflo",
        "name": "Ruflo",
        "repo_url": "https://github.com/ruvnet/ruflo",
        "category": "Agenti AI & Automazione",
        "tagline": "Coordinatore multi-agente con memoria condivisa per far lavorare più agenti AI insieme sullo stesso progetto.",
        "simple_explanation": (
            "Quando chiedi a un singolo agente AI di fare un lavoro molto lungo e complesso, spesso perde il filo o "
            "dimentica cosa aveva deciso prima. Ruflo fa da 'direttore dei lavori': divide un compito grande tra più "
            "agenti specializzati, mantiene una memoria comune (così non ripetono gli stessi errori) e imposta regole di sicurezza."
        ),
        "specs": {
            "linguaggio": "TypeScript / Node.js",
            "sistemi_operativi": "Windows, macOS, Linux",
            "costo": "Gratuito (Open Source - attenzione però al consumo di token AI)",
            "supporto_mcp": "Sì (orchestratore attorno a Claude Code / Codex / MCP)",
            "difficolta": "Media"
        },
        "compatible_apps": [
            "Piattaforme che eseguono flussi di lavoro AI complessi in più passaggi",
            "Sistemi automatici di generazione/revisione codice o report",
            "Backend multi-agente con memoria a lungo termine (RAG)",
            "Automazioni aziendali con regole di controllo rigorose"
        ],
        "tech_keywords": ["agent", "swarm", "orchestration", "typescript", "node", "rag", "memory", "workflow", "llm"],
        "cost_saving": "Evita di dover programmare da zero code di messaggi, memoria condivisa e coordinamento tra agenti AI.",
        "honest_tradeoffs": (
            "Far lavorare una squadra di 4-5 agenti in contemporanea consuma molti più crediti/token AI rispetto a un "
            "singolo agente normale. Per progetti piccoli o semplici è eccessivo (aggiunge complessità inutile); conviene "
            "solo quando hai compiti pesanti divisibili in parallelo."
        ),
        "install_guide": (
            "1. Assicurati di avere Node.js 20+ installato.\n"
            "2. Consulta il repository ufficiale https://github.com/ruvnet/ruflo per installare la CLI:\n"
            "   npx ruflo@latest init\n"
            "3. Definisci i ruoli degli agenti e i limiti di budget prima di avviare un flusso automatico."
        )
    }
]


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                repo_url TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Generale',
                tagline TEXT NOT NULL,
                simple_explanation TEXT NOT NULL,
                specs_json TEXT NOT NULL DEFAULT '{}',
                compatible_apps_json TEXT NOT NULL DEFAULT '[]',
                tech_keywords_json TEXT NOT NULL DEFAULT '[]',
                cost_saving TEXT NOT NULL DEFAULT '',
                honest_tradeoffs TEXT NOT NULL DEFAULT '',
                install_guide TEXT NOT NULL DEFAULT '',
                stars INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );
            """
        )

        count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        if count == 0:
            now = datetime.now(timezone.utc).isoformat()
            for item in SEED_SKILLS:
                conn.execute(
                    """
                    INSERT INTO skills (
                        slug, name, repo_url, category, tagline, simple_explanation,
                        specs_json, compatible_apps_json, tech_keywords_json,
                        cost_saving, honest_tradeoffs, install_guide, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["slug"],
                        item["name"],
                        item["repo_url"],
                        item["category"],
                        item["tagline"],
                        item["simple_explanation"],
                        json.dumps(item["specs"], ensure_ascii=False),
                        json.dumps(item["compatible_apps"], ensure_ascii=False),
                        json.dumps(item["tech_keywords"], ensure_ascii=False),
                        item["cost_saving"],
                        item["honest_tradeoffs"],
                        item["install_guide"],
                        now,
                    ),
                )
    conn.close()


def _row_to_skill(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "slug": row["slug"],
        "name": row["name"],
        "repo_url": row["repo_url"],
        "category": row["category"],
        "tagline": row["tagline"],
        "simple_explanation": row["simple_explanation"],
        "specs": json.loads(row["specs_json"] or "{}"),
        "compatible_apps": json.loads(row["compatible_apps_json"] or "[]"),
        "tech_keywords": json.loads(row["tech_keywords_json"] or "[]"),
        "cost_saving": row["cost_saving"],
        "honest_tradeoffs": row["honest_tradeoffs"],
        "install_guide": row["install_guide"],
        "stars": row["stars"],
        "created_at": row["created_at"],
    }


def list_skills(query: str = "", category: str = "") -> list[dict]:
    conn = get_connection()
    sql = "SELECT * FROM skills WHERE 1=1"
    params: list = []
    if category and category.lower() != "tutte":
        sql += " AND LOWER(category) = LOWER(?)"
        params.append(category)
    if query:
        q = f"%{query.strip()}%"
        sql += """ AND (
            name LIKE ? OR tagline LIKE ? OR simple_explanation LIKE ?
            OR compatible_apps_json LIKE ? OR tech_keywords_json LIKE ? OR category LIKE ?
        )"""
        params.extend([q, q, q, q, q, q])
    sql += " ORDER BY id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_row_to_skill(r) for r in rows]


def get_skill_by_id_or_slug(identifier: str | int) -> dict | None:
    conn = get_connection()
    if str(identifier).isdigit():
        row = conn.execute("SELECT * FROM skills WHERE id = ?", (int(identifier),)).fetchone()
    else:
        row = conn.execute("SELECT * FROM skills WHERE LOWER(slug) = LOWER(?)", (str(identifier),)).fetchone()
    conn.close()
    return _row_to_skill(row) if row else None


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "skill"


def add_or_update_skill(data: dict) -> dict:
    name = (data.get("name") or "").strip()
    repo_url = (data.get("repo_url") or "").strip()
    if not name or not repo_url:
        raise ValueError("Nome e link del repository sono obbligatori.")

    slug = slugify(data.get("slug") or name)
    category = (data.get("category") or "Generale").strip()
    tagline = (data.get("tagline") or name).strip()
    simple_explanation = (data.get("simple_explanation") or tagline).strip()
    specs = data.get("specs") if isinstance(data.get("specs"), dict) else {}
    compatible_apps = data.get("compatible_apps") if isinstance(data.get("compatible_apps"), list) else []
    tech_keywords = data.get("tech_keywords") if isinstance(data.get("tech_keywords"), list) else []
    cost_saving = (data.get("cost_saving") or "").strip()
    honest_tradeoffs = (data.get("honest_tradeoffs") or "").strip()
    install_guide = (data.get("install_guide") or "").strip()
    stars = int(data.get("stars") or 0)
    now = datetime.now(timezone.utc).isoformat()

    conn = get_connection()
    with conn:
        existing = conn.execute("SELECT id FROM skills WHERE slug = ?", (slug,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE skills SET
                    name=?, repo_url=?, category=?, tagline=?, simple_explanation=?,
                    specs_json=?, compatible_apps_json=?, tech_keywords_json=?,
                    cost_saving=?, honest_tradeoffs=?, install_guide=?, stars=?
                WHERE slug=?
                """,
                (
                    name, repo_url, category, tagline, simple_explanation,
                    json.dumps(specs, ensure_ascii=False),
                    json.dumps(compatible_apps, ensure_ascii=False),
                    json.dumps(tech_keywords, ensure_ascii=False),
                    cost_saving, honest_tradeoffs, install_guide, stars, slug
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO skills (
                    slug, name, repo_url, category, tagline, simple_explanation,
                    specs_json, compatible_apps_json, tech_keywords_json,
                    cost_saving, honest_tradeoffs, install_guide, stars, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    slug, name, repo_url, category, tagline, simple_explanation,
                    json.dumps(specs, ensure_ascii=False),
                    json.dumps(compatible_apps, ensure_ascii=False),
                    json.dumps(tech_keywords, ensure_ascii=False),
                    cost_saving, honest_tradeoffs, install_guide, stars, now
                ),
            )
    conn.close()
    return get_skill_by_id_or_slug(slug)  # type: ignore


def delete_skill(skill_id: int) -> bool:
    conn = get_connection()
    with conn:
        cur = conn.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
    conn.close()
    return cur.rowcount > 0


def fetch_github_metadata(repo_url: str) -> dict:
    """Legge i dati pubblici da un link GitHub per pre-compilare la scheda Blooder."""
    match = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", repo_url)
    if not match:
        raise ValueError("Inserisci un link GitHub valido (es. https://github.com/utente/progetto).")

    owner, repo = match.group(1), match.group(2).removesuffix(".git")
    headers = {"User-Agent": "Blooder-Skill-Library/1.0", "Accept": "application/vnd.github+json"}

    req = urllib.request.Request(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ValueError(f"Impossibile leggere il repository su GitHub (codice {e.code}).") from e
    except Exception as e:
        raise ValueError(f"Errore di connessione a GitHub: {e}") from e

    # Prova a estrarre qualche comando di installazione dal README
    readme_snippet = ""
    try:
        readme_req = urllib.request.Request(
            f"https://api.github.com/repos/{owner}/{repo}/readme",
            headers={**headers, "Accept": "application/vnd.github.raw+json"},
        )
        with urllib.request.urlopen(readme_req, timeout=8) as r_resp:
            raw_readme = r_resp.read().decode("utf-8", errors="ignore")
            code_blocks = re.findall(r"```(?:bash|sh|shell|zsh|powershell)?\n(.*?)```", raw_readme, re.DOTALL)
            for block in code_blocks:
                if any(cmd in block for cmd in ("pip ", "npm ", "npx ", "uv ", "git clone", "docker", "cargo ", "brew ")):
                    readme_snippet = block.strip()[:500]
                    break
    except Exception:
        pass

    language = meta.get("language") or "Multi-linguaggio"
    license_info = (meta.get("license") or {}).get("spdx_id") or "Open Source"
    topics = meta.get("topics") or []
    description = meta.get("description") or f"Repository open-source {owner}/{repo}"

    install_default = (
        f"1. Clona il repository:\n   git clone https://github.com/{owner}/{repo}.git\n"
        + (f"\n2. Comandi rilevati dal README:\n{readme_snippet}" if readme_snippet else "")
    )

    return {
        "name": meta.get("name") or repo,
        "repo_url": f"https://github.com/{owner}/{repo}",
        "category": "Nuova Skill",
        "tagline": description,
        "simple_explanation": (
            f"{description}\n\n(Puoi personalizzare qui in parole semplici cosa fa questa skill e perché è utile)."
        ),
        "specs": {
            "linguaggio": language,
            "sistemi_operativi": "Windows, macOS, Linux",
            "costo": f"Gratuito ({license_info})",
            "difficolta": "Media",
        },
        "compatible_apps": [f"Progetti basati su {language}"] + [f"App tema: {t}" for t in topics[:3]],
        "tech_keywords": [language.lower()] + [t.lower() for t in topics],
        "cost_saving": "Alternativa gratuita open-source a servizi simili a pagamento.",
        "honest_tradeoffs": "Richiede configurazione autonoma rispetto a un servizio cloud chiavi in mano.",
        "install_guide": install_default,
        "stars": int(meta.get("stargazers_count") or 0),
    }

