import json
import mimetypes
import sys
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from blooder_db import (
    add_or_update_blooderskill,
    add_or_update_skill,
    delete_blooderskill,
    delete_skill,
    fetch_github_metadata,
    get_blooderskill_by_id_or_slug,
    get_skill_by_id_or_slug,
    init_db,
    list_blooderskills,
    list_skills,
    sync_blooderskills_disk,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
PORT = 8765

mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("image/svg+xml", ".svg")


class BlooderHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def _send_json(self, data: object, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/api/skills":
            q = (qs.get("q") or [""])[0]
            cat = (qs.get("category") or [""])[0]
            kind = (qs.get("kind") or [""])[0]
            self._send_json({"skills": list_skills(q, cat, kind)})
            return

        if path.startswith("/api/skills/"):
            ident = path.removeprefix("/api/skills/").strip("/")
            sk = get_skill_by_id_or_slug(ident)
            if not sk:
                self._send_json({"error": "Skill non trovata"}, HTTPStatus.NOT_FOUND)
            else:
                self._send_json(sk)
            return

        if path == "/api/blooderskills":
            q = (qs.get("q") or [""])[0]
            sec = (qs.get("sector") or [""])[0]
            self._send_json({"blooderskills": list_blooderskills(q, sec)})
            return

        if path.startswith("/api/blooderskills/"):
            ident = path.removeprefix("/api/blooderskills/").strip("/")
            bs = get_blooderskill_by_id_or_slug(ident)
            if not bs:
                self._send_json({"error": "Blooderskill non trovata"}, HTTPStatus.NOT_FOUND)
            else:
                self._send_json(bs)
            return

        # File statici della libreria (inclusi font .woff2, icone .svg, stili)
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        file_path = (STATIC_DIR / rel).resolve()
        if not str(file_path).startswith(str(STATIC_DIR.resolve())) or not file_path.is_file():
            self._send_json({"error": "Risorsa non trovata"}, HTTPStatus.NOT_FOUND)
            return

        mime, _ = mimetypes.guess_type(str(file_path))
        mime = mime or "application/octet-stream"
        if mime.startswith("text/") or mime in ("application/javascript", "application/json", "image/svg+xml"):
            content_type = f"{mime}; charset=utf-8"
        else:
            content_type = mime

        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/skills":
                saved = add_or_update_skill(payload)
                self._send_json(saved, HTTPStatus.CREATED)
            elif path == "/api/blooderskills":
                saved = add_or_update_blooderskill(payload)
                self._send_json(saved, HTTPStatus.CREATED)
            elif path == "/api/github-preview":
                preview = fetch_github_metadata(payload.get("repo_url", ""))
                self._send_json(preview)
            else:
                self._send_json({"error": "Endpoint sconosciuto"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if path.startswith("/api/skills/"):
            sid = int(path.removeprefix("/api/skills/").strip("/"))
            ok = delete_skill(sid)
            self._send_json({"deleted": ok})
        elif path.startswith("/api/blooderskills/"):
            bid = int(path.removeprefix("/api/blooderskills/").strip("/"))
            ok = delete_blooderskill(bid)
            self._send_json({"deleted": ok})
        else:
            self._send_json({"error": "Endpoint sconosciuto"}, HTTPStatus.NOT_FOUND)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    init_db()
    sync_blooderskills_disk()
    no_browser = "--no-browser" in sys.argv
    server = ThreadingHTTPServer(("127.0.0.1", PORT), BlooderHandler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"[Blooder] Libreria attiva su {url}")
    if not no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nChiusura Blooder.")
        server.server_close()


if __name__ == "__main__":
    main()
