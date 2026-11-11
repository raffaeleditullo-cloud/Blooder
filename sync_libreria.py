import json
import re
import subprocess
import sys
from pathlib import Path

from blooder_db import (
    BASE_DIR,
    GITHUB_REPO,
    get_connection,
    init_db,
    list_blooderskills,
    list_skills,
    sync_blooderskills_disk,
)

# Pattern rigorosi per intercettare vere chiavi private, API key o token dimenticati nei file
SECRET_PATTERNS = [
    ("Chiave OpenAI / API sk-", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("Token GitHub ghp_/github_pat_", re.compile(r"\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("Chiave Google AIza", re.compile(r"\bAIza[0-9A-Za-z_-]{32,}\b")),
    ("Token Slack xox", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{20,}\b")),
    ("Chiave AWS AKIA", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Chiave Privata PEM/SSH", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)?PRIVATE KEY-----")),
    ("Chiave Anthropic sk-ant-", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
]

BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".ttf", ".db", ".sqlite"}


def check_db_integrity() -> None:
    conn = get_connection()
    ok = conn.execute("PRAGMA integrity_check").fetchone()[0]
    conn.close()
    if ok != "ok":
        raise RuntimeError(f"Integrità database fallita: {ok}")


def build_readme(skills: list[dict], tools: list[dict], blooderskills: list[dict]) -> str:
    lines = [
        '<div align="center">',
        '  <img src="static/hero-banner.svg" alt="Blooder — Libreria Aperta Skill, Strumenti &amp; Blooderskills" width="100%" />',
        "",
        "  <br />",
        "",
        f'  <img src="https://img.shields.io/badge/Libreria_Skill-{len(skills)}_attive-ff1236?style=for-the-badge&labelColor=140407" alt="Skill attive" />',
        f'  <img src="https://img.shields.io/badge/Strumenti-{len(tools)}_attivi-ff1236?style=for-the-badge&labelColor=140407" alt="Strumenti attivi" />',
        f'  <img src="https://img.shields.io/badge/Blooderskills-{len(blooderskills)}_moduli-10b981?style=for-the-badge&labelColor=140407" alt="Blooderskills" />',
        '  <img src="https://img.shields.io/badge/Licenza-MIT-fbeef0?style=for-the-badge&labelColor=140407" alt="MIT License" />',
        '  <img src="https://img.shields.io/badge/Python-3.10+-ff4d63?style=for-the-badge&labelColor=140407" alt="Python 3.10+" />',
        "</div>",
        "",
        "---",
        "",
        "## Cos'è Blooder",
        "",
        "**Blooder** è una libreria interattiva locale e open-source dal design **Red Matrix** progettata per raccogliere, filtrare e potenziare il meglio dell'ecosistema per **Agenti AI e sviluppo moderno**, senza dipendere da database cloud esterni o dipendenze pesanti.",
        "",
        "L'architettura è divisa in **tre reparti complementari**:",
        "",
        "1. **Libreria Skill** — Selezione ragionata delle migliori skill open-source per agenti AI, spiegate senza gergo inutile, con pro, contro onesti e risparmio reale.",
        "2. **Strumenti** — Utility operative e CLI ad alto impatto per automatizzare desktop, API, sicurezza e mobile.",
        "3. **Blooderskills** — Il laboratorio originale di **Blooder**: moduli specialistici verticali (*\"il pezzo in più\"*) costruiti per settore piattaforma (Fatturazione, Vendita, Guide, Automazione), collaudati sul campo ed esportati automaticamente in [`skills/`](skills/) per l'installazione diretta.",
        "",
        "---",
        "",
        "## Blooderskills pubblicate (Moduli originali)",
        "",
    ]

    if blooderskills:
        lines.extend([
            "Installa qualsiasi modulo originale **Blooderskill** direttamente nel tuo agente AI con:",
            "",
            "```bash",
            f"npx skills add {GITHUB_REPO} --skill <nome-skill>",
            "```",
            "",
            "| Modulo | Settore Piattaforma | Potenzia | Stato | Descrizione |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])
        for b in blooderskills:
            st = "Collaudata" if b["status"] == "collaudata" else "In test"
            bases = ", ".join(b["base_skills"]) if b.get("base_skills") else "Autonoma"
            lines.append(
                f"| **[`{b['name']}`](skills/{b['slug']}/SKILL.md)** | `{b['sector']}` | {bases} | {st} | {b['tagline']} |"
            )
        lines.append("")
    else:
        lines.extend([
            "> Nessun modulo verticale ancora pubblicato in [`skills/`](skills/). Ogni nuova **Blooderskill** creata nell'interfaccia comparirà automaticamente in questa tabella e sarà installabile con:",
            "> ```bash",
            f"> npx skills add {GITHUB_REPO} --skill <nome-skill>",
            "> ```",
            "",
        ])

    lines.extend([
        "---",
        "",
        f"## Libreria Skill ({len(skills)} selezionate)",
        "",
        "| Skill | Categoria | Cosa fa in una riga |",
        "| :--- | :--- | :--- |",
    ])
    for s in skills:
        lines.append(f"| **[{s['name']}]({s['repo_url']})** | `{s['category']}` | {s['tagline']} |")

    lines.extend([
        "",
        "---",
        "",
        f"## Strumenti Operativi ({len(tools)} selezionati)",
        "",
        "| Strumento | Categoria | Cosa fa in una riga |",
        "| :--- | :--- | :--- |",
    ])
    for t in tools:
        lines.append(f"| **[{t['name']}]({t['repo_url']})** | `{t['category']}` | {t['tagline']} |")

    lines.extend([
        "",
        "---",
        "",
        "## Avvio rapido in locale (Zero dipendenze esterne)",
        "",
        "Blooder usa esclusivamente la libreria standard di **Python 3.10+** (`http.server` + `sqlite3`) con interfaccia **Red Matrix** e font locali inclusi.",
        "",
        "```bash",
        f"git clone https://github.com/{GITHUB_REPO}.git",
        "cd Blooder",
        "python app.py",
        "```",
        "",
        "- Su Windows ti basta fare doppio click su **`avvia_blooder.bat`** (apre automaticamente `http://127.0.0.1:8765`).",
        "- Per verificare il database, aggiornare il catalogo JSON/README, controllare l'assenza di chiavi segrete e sincronizzare GitHub in un colpo solo, usa **`salva_progetto.bat`**.",
        "",
        "---",
        "",
        "## Sicurezza & Privacy by Design",
        "",
        "- **Zero telemetria e zero cloud:** tutto gira su `127.0.0.1` e salva in `blooder.db` + `backup_libreria.json`.",
        "- **Scudo anti-segreti integrato:** prima di ogni salvataggio Git, `sync_libreria.py` analizza i file tracciati e blocca automaticamente il commit se rileva chiavi private o token API.",
        "",
        "---",
        "",
        "## Licenza",
        "",
        "Distribuito sotto licenza **[MIT](LICENSE)** — Copyright (c) 2026 **Raffaele Di Tullo**.",
        "Le skill e gli strumenti di terze parti catalogati nella *Libreria Skill* e negli *Strumenti* appartengono ai rispettivi autori e mantengono le licenze dei relativi repository ufficiali.",
        "",
    ])
    return "\n".join(lines)


def scan_for_secrets() -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=BASE_DIR,
        text=True,
    )
    findings: list[str] = []
    for rel in out.splitlines():
        p = BASE_DIR / rel
        if not p.is_file() or p.suffix.lower() in BINARY_EXTS:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for label, regex in SECRET_PATTERNS:
            m = regex.search(text)
            if m:
                snippet = m.group(0)[:10] + "..."
                findings.append(f"{rel} -> {label} ({snippet})")
    return findings


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    init_db()
    check_db_integrity()

    skills = list_skills(kind="skill")
    tools = list_skills(kind="tool")
    blooderskills = list_blooderskills()

    exported_files = sync_blooderskills_disk()

    backup_data = {
        "skills": skills,
        "tools": tools,
        "blooderskills": blooderskills,
    }
    (BASE_DIR / "backup_libreria.json").write_text(
        json.dumps(backup_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    readme_text = build_readme(skills, tools, blooderskills)
    (BASE_DIR / "README.md").write_text(readme_text, encoding="utf-8")

    findings = scan_for_secrets()
    if findings:
        print("[BLOCCO SICUREZZA] Rilevate possibili chiavi segrete nei file destinati a Git:")
        for f in findings:
            print(f"  - {f}")
        return 2

    print(
        f"[Blooder OK] DB integro | {len(skills)} skill, {len(tools)} strumenti, "
        f"{len(blooderskills)} Blooderskills ({len(exported_files)} file in skills/) | Zero chiavi segrete rilevate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
