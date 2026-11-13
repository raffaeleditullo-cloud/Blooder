"""
attiva_arsenale.py — Monta in locale (.agents/vendor_skills/) le vere skill operative
selezionate nella libreria di Blooder, così Antigravity, Claude Code, Codex e Cursor
le hanno attive e pronte all'uso in ogni decisione di progetto.
Zero dipendenze esterne (solo libreria standard Python).
"""

import io
import shutil
import urllib.request
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENDOR_DIR = BASE_DIR / ".agents" / "vendor_skills"

# Mappa chirurgica: (owner/repo, branch, [(sottocartella_nel_repo, nome_cartella_destinazione), ...])
ARSENAL_SOURCES: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "multica-ai/andrej-karpathy-skills",
        "main",
        [("skills/karpathy-guidelines", "karpathy-guidelines")],
    ),
    (
        "Nanako0129/sepia",
        "main",
        [("skills/sepia", "sepia")],
    ),
    (
        "Jakeschincariol/founder-skill",
        "main",
        [
            ("skills/founder-board", "founder-board"),
            ("skills/founder-cfo", "founder-cfo"),
            ("skills/founder-pricing", "founder-pricing"),
            ("skills/founder-consumer", "founder-consumer"),
            ("skills/founder-offer", "founder-offer"),
        ],
    ),
    (
        "mattpocock/skills",
        "main",
        [("skills/productivity/teach", "teach")],
    ),
    (
        "wheresryan22/anatomy",
        "main",
        [("", "anatomy")],
    ),
    (
        "coreyhaines31/marketingskills",
        "main",
        [
            ("skills/marketing-psychology", "marketing-psychology"),
            ("skills/cro", "cro"),
        ],
    ),
    (
        "Egonex-AI/Understand-Anything",
        "main",
        [
            ("understand-anything-plugin/skills/understand", "understand"),
            ("understand-anything-plugin/skills/understand-diff", "understand-diff"),
        ],
    ),
    (
        "usestrix/strix",
        "main",
        [
            ("skills/find-security-vulnerabilities-in-code", "find-security-vulnerabilities-in-code"),
            ("skills/penetration-testing-with-strix", "penetration-testing-with-strix"),
        ],
    ),
    (
        "bradautomates/claude-video",
        "main",
        [("skills/watch", "watch")],
    ),
    (
        "kalil0321/reverse-api-engineer",
        "main",
        [("skills/reverse-api-engineer", "reverse-api-engineer")],
    ),
    (
        "Panniantong/agent-reach",
        "main",
        [("agent_reach/skill", "agent-reach")],
    ),
    (
        "Tejashmakwana/motionmaxxing",
        "main",
        [("", "motionmaxxing")],
    ),
    (
        "ayghri/i-have-adhd",
        "main",
        [("skills/i-have-adhd", "i-have-adhd")],
    ),
]

SKIP_ROOT_DIRS_FOR_FULL_REPO = {".github", "tests", "evals", "docs"}


def download_zip(repo: str, branch: str) -> bytes:
    url = f"https://codeload.github.com/{repo}/zip/refs/heads/{branch}"
    req = urllib.request.Request(url, headers={"User-Agent": "Blooder-Arsenal-Installer/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def extract_skill_from_zip(zf: zipfile.ZipFile, root_prefix: str, src_subpath: str, dest_dir: Path) -> int:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    full_prefix = f"{root_prefix}/{src_subpath}".rstrip("/") + "/"
    count = 0
    for info in zf.infolist():
        if info.is_dir():
            continue
        if not info.filename.startswith(full_prefix):
            continue
        rel = info.filename[len(full_prefix):]
        if not rel:
            continue
        if src_subpath == "":
            top = rel.split("/", 1)[0]
            if top in SKIP_ROOT_DIRS_FOR_FULL_REPO or top.startswith(".git"):
                continue
        target_path = (dest_dir / rel).resolve()
        if not str(target_path).startswith(str(dest_dir.resolve())):
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(zf.read(info.filename))
        count += 1
    return count


def verify_skill_md(dest_dir: Path) -> bool:
    md = dest_dir / "SKILL.md"
    if not md.is_file():
        return False
    txt = md.read_text(encoding="utf-8", errors="ignore").lstrip()
    return txt.startswith("---") and "name:" in txt[:600] and "description:" in txt[:1200]


def main() -> None:
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    installed = []
    failed = []

    print("[Blooder] Scaricamento e attivazione skill operative in .agents/vendor_skills/ ...")
    for repo, branch, mappings in ARSENAL_SOURCES:
        try:
            raw = download_zip(repo, branch)
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                names = zf.namelist()
                if not names:
                    raise RuntimeError("Archivio ZIP vuoto")
                root_prefix = names[0].split("/", 1)[0]
                for src_subpath, dest_name in mappings:
                    dest_dir = VENDOR_DIR / dest_name
                    n_files = extract_skill_from_zip(zf, root_prefix, src_subpath, dest_dir)
                    if verify_skill_md(dest_dir):
                        installed.append((dest_name, repo, n_files))
                        print(f"  [OK] {dest_name:<38} <- {repo} ({n_files} file)")
                    else:
                        failed.append((dest_name, repo, "SKILL.md mancante o frontmatter non valido"))
                        print(f"  [ERR] {dest_name}: SKILL.md mancante o non valido")
        except Exception as exc:
            for _, dest_name in mappings:
                failed.append((dest_name, repo, str(exc)))
            print(f"  [ERR] {repo}: {exc}")

    print("-" * 72)
    print(f"[Blooder] Skill operative attive: {len(installed)} | Errori: {len(failed)}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
