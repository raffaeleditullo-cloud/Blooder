#!/usr/bin/env python3
"""Ricerca e download gratuito di effetti sonori CC0 dall'API pubblica di Openverse (senza API key)."""
import json
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://api.openverse.org/v1/audio/"


def search_cc0(query: str, page_size: int = 5) -> list[dict]:
    params = urllib.parse.urlencode({
        "q": query,
        "license": "cc0",
        "page_size": page_size,
    })
    req = urllib.request.Request(
        f"{API_URL}?{params}",
        headers={"User-Agent": "BlooderReelKit/1.0 (+https://github.com/raffaeleditullo-cloud/Blooder)"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [
        {
            "id": r.get("id"),
            "title": r.get("title"),
            "url": r.get("url"),
            "duration_ms": r.get("duration"),
            "license": r.get("license"),
        }
        for r in data.get("results", [])
        if r.get("url")
    ]


def download_first_cc0(query: str, out_dir: Path) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = "".join(c if c.isalnum() else "_" for c in query.lower()).strip("_")
    for item in search_cc0(query, page_size=5):
        ext = Path(urllib.parse.urlparse(item["url"]).path).suffix or ".mp3"
        dest = out_dir / f"{slug}{ext}"
        if dest.exists() and dest.stat().st_size > 1000:
            return dest
        try:
            req = urllib.request.Request(item["url"], headers={"User-Agent": "BlooderReelKit/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                dest.write_bytes(r.read())
            if dest.stat().st_size > 1000:
                return dest
        except Exception:
            continue
    return None


if __name__ == "__main__":
    results = search_cc0("whoosh", page_size=3)
    print(json.dumps(results, indent=2))
