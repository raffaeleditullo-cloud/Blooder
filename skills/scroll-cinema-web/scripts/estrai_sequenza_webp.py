"""
estrai_sequenza_webp.py — Motore deterministico per Scroll Cinema Web (Blooderskill)
Trasforma un video di transizione AI (.mp4 / .mov / .webm) in una sequenza leggera
di fotogrammi .webp ottimizzati per scorrimento fluido a 60fps su HTML5 <canvas>,
verificando il budget di peso in MB e generando facoltativamente una pagina HTML
pronta all'uso con fisica morbida (Lerp), Retina DPR e fallback accessibilità.

Zero dipendenze Python esterne (richiede solo Python 3.10+ e FFmpeg nel PATH).
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


HTML_STARTER_TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    :root {{
      --bg: #070709;
      --fg: #f5f5f7;
      --muted: rgba(245, 245, 247, 0.68);
      --accent: #ff1236;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      background: var(--bg);
      color: var(--fg);
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      overscroll-behavior: none;
    }}
    .scroll-stage {{
      position: relative;
      height: {scroll_vh}vh;
    }}
    .sticky-viewport {{
      position: sticky;
      top: 0;
      width: 100%;
      height: 100vh;
      overflow: hidden;
      background: var(--bg);
    }}
    canvas#cinema-canvas {{
      width: 100%;
      height: 100%;
      display: block;
    }}
    .vignette {{
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: radial-gradient(circle at center, transparent 45%, rgba(0, 0, 0, 0.72) 100%),
                  linear-gradient(to top, rgba(7, 7, 9, 0.85) 0%, transparent 28%, rgba(7, 7, 9, 0.45) 100%);
    }}
    .beat {{
      position: absolute;
      left: clamp(1.5rem, 6vw, 6rem);
      bottom: clamp(3rem, 10vh, 7rem);
      max-width: 38rem;
      opacity: 0;
      transform: translateY(24px);
      transition: opacity 0.35s ease, transform 0.35s ease;
      pointer-events: none;
    }}
    .beat.is-active {{
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }}
    .beat h1, .beat h2 {{
      font-size: clamp(2.1rem, 5vw, 4.2rem);
      line-height: 1.04;
      letter-spacing: -0.03em;
      margin-bottom: 0.75rem;
    }}
    .beat p {{
      font-size: clamp(1rem, 1.4vw, 1.2rem);
      line-height: 1.55;
      color: var(--muted);
      margin-bottom: 1.4rem;
    }}
    .cta-btn {{
      display: inline-block;
      padding: 0.9rem 1.6rem;
      border-radius: 999px;
      background: var(--fg);
      color: var(--bg);
      font-weight: 600;
      text-decoration: none;
    }}
    .loader-bar {{
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      width: 0%;
      background: var(--accent);
      z-index: 50;
      transition: width 0.15s linear, opacity 0.4s ease;
    }}
    @media (prefers-reduced-motion: reduce) {{
      .scroll-stage {{ height: 100vh; }}
      .beat {{ opacity: 1 !important; transform: none !important; }}
    }}
  </style>
</head>
<body>
  <div class="loader-bar" id="loader-bar"></div>

  <section class="scroll-stage" id="scroll-stage">
    <div class="sticky-viewport">
      <canvas id="cinema-canvas" aria-label="{title}"></canvas>
      <div class="vignette"></div>

      <div class="beat is-active" data-start="0.00" data-end="0.30">
        <h1>Meglio del giorno in cui l'hai ritirata.</h1>
        <p>Scorri per attraversare la scena: sequenza fotogrammi WebP ad alta efficienza sincronizzata a 60fps.</p>
        <a href="#contatti" class="cta-btn">Richiedi Preventivo</a>
      </div>

      <div class="beat" data-start="0.36" data-end="0.68">
        <h2>Precisione su ogni dettaglio.</h2>
        <p>Nessun modello 3D pesante da scaricare: caricamento progressivo istantaneo anche su smartphone.</p>
      </div>

      <div class="beat" data-start="0.74" data-end="1.01">
        <h2>Pronto per il lancio.</h2>
        <p>Personalizza testi, font e pulsanti mantenendo intatto il motore fluido su Canvas.</p>
        <a href="#contatti" class="cta-btn">Prenota Ora</a>
      </div>
    </div>
  </section>

  <script>
    (async function () {{
      const res = await fetch('./frames.json');
      const manifest = await res.json();
      const isMobile = window.matchMedia('(max-width: 768px)').matches && manifest.mobile_frames.length > 0;
      const urls = isMobile ? manifest.mobile_frames : manifest.desktop_frames;
      const total = urls.length;

      const canvas = document.getElementById('cinema-canvas');
      const ctx = canvas.getContext('2d', {{ alpha: false }});
      const stage = document.getElementById('scroll-stage');
      const loader = document.getElementById('loader-bar');
      const beats = Array.from(document.querySelectorAll('.beat'));
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      const images = new Array(total);
      let loaded = 0;
      let targetProgress = 0;
      let smoothProgress = 0;
      let lastDrawnIndex = -1;

      function resizeCanvas() {{
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.floor(window.innerWidth * dpr);
        canvas.height = Math.floor(window.innerHeight * dpr);
        lastDrawnIndex = -1;
      }}

      function drawCover(img) {{
        if (!img || !img.complete || !img.naturalWidth) return;
        const cw = canvas.width, ch = canvas.height;
        const iw = img.naturalWidth, ih = img.naturalHeight;
        const scale = Math.max(cw / iw, ch / ih);
        const nw = iw * scale, nh = ih * scale;
        const ox = (cw - nw) * 0.5, oy = (ch - nh) * 0.5;
        ctx.drawImage(img, ox, oy, nw, nh);
      }}

      function preloadAll() {{
        urls.forEach((u, idx) => {{
          const img = new Image();
          img.decoding = 'async';
          img.onload = () => {{
            loaded++;
            loader.style.width = ((loaded / total) * 100).toFixed(1) + '%';
            if (idx === 0) drawCover(img);
            if (loaded === total) setTimeout(() => {{ loader.style.opacity = '0'; }}, 250);
          }};
          img.src = u;
          images[idx] = img;
        }});
      }}

      function onScroll() {{
        const rect = stage.getBoundingClientRect();
        const scrollable = Math.max(1, stage.offsetHeight - window.innerHeight);
        targetProgress = Math.min(1, Math.max(0, -rect.top / scrollable));
      }}

      function updateBeats(p) {{
        for (const b of beats) {{
          const s = parseFloat(b.dataset.start), e = parseFloat(b.dataset.end);
          b.classList.toggle('is-active', p >= s && p <= e);
        }}
      }}

      function tick() {{
        if (!reducedMotion) {{
          smoothProgress += (targetProgress - smoothProgress) * 0.12;
          const idx = Math.min(total - 1, Math.max(0, Math.round(smoothProgress * (total - 1))));
          if (idx !== lastDrawnIndex && images[idx] && images[idx].complete) {{
            drawCover(images[idx]);
            lastDrawnIndex = idx;
          }}
          updateBeats(smoothProgress);
          requestAnimationFrame(tick);
        }}
      }}

      window.addEventListener('resize', resizeCanvas, {{ passive: true }});
      window.addEventListener('scroll', onScroll, {{ passive: true }});
      resizeCanvas();
      preloadAll();
      onScroll();
      if (!reducedMotion) requestAnimationFrame(tick);
    }})();
  </script>
</body>
</html>
"""


def probe_video(video_path: Path) -> dict:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"duration_s": 0.0, "width": 0, "height": 0}
    cmd = [
        ffprobe, "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "json",
        str(video_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        return {"duration_s": 0.0, "width": 0, "height": 0}
    data = json.loads(res.stdout or "{}")
    streams = data.get("streams") or [{}]
    fmt = data.get("format") or {}
    return {
        "duration_s": round(float(fmt.get("duration") or 0.0), 3),
        "width": int(streams[0].get("width") or 0),
        "height": int(streams[0].get("height") or 0),
    }


def extract_webp_sequence(
    ffmpeg: str,
    video_path: Path,
    out_folder: Path,
    fps: int,
    max_width: int,
    quality: int,
    max_frames: int,
) -> list[Path]:
    if out_folder.exists():
        shutil.rmtree(out_folder)
    out_folder.mkdir(parents=True, exist_ok=True)

    vf = f"fps={fps},scale='min({max_width},iw)':-2:flags=lanczos"
    pattern = out_folder / "frame_%04d.webp"
    cmd = [
        ffmpeg, "-y", "-v", "error",
        "-i", str(video_path),
        "-vf", vf,
        "-frames:v", str(max_frames),
        "-vcodec", "libwebp",
        "-lossless", "0",
        "-compression_level", "4",
        "-q:v", str(quality),
        "-an",
        str(pattern),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Errore FFmpeg durante estrazione WebP: {res.stderr.strip()}")
    return sorted(out_folder.glob("frame_*.webp"))


def folder_size_mb(files: list[Path]) -> float:
    return round(sum(f.stat().st_size for f in files) / (1024 * 1024), 2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Estrae sequenze WebP desktop/mobile e genera starter Scroll Cinema Web.")
    parser.add_argument("video", help="Percorso del video sorgente (.mp4, .mov, .webm)")
    parser.add_argument("--out", default="./scroll_cinema_build", help="Cartella di destinazione")
    parser.add_argument("--fps", type=int, default=24, help="Fotogrammi al secondo da estrarre (consigliato: 20-30)")
    parser.add_argument("--max-frames", type=int, default=160, help="Numero massimo di fotogrammi totali (default: 160)")
    parser.add_argument("--desktop-width", type=int, default=1600, help="Larghezza max desktop in px (default: 1600)")
    parser.add_argument("--mobile-width", type=int, default=860, help="Larghezza max mobile in px (default: 860)")
    parser.add_argument("--quality", type=int, default=80, help="Qualità WebP 1-100 (default: 80)")
    parser.add_argument("--no-mobile", action="store_true", help="Non generare la sequenza ridotta per smartphone")
    parser.add_argument("--generate-html", action="store_true", help="Genera anche index.html pronto da aprire")
    parser.add_argument("--title", default="Scroll Cinema Experience", help="Titolo pagina HTML")
    parser.add_argument("--scroll-vh", type=int, default=420, help="Altezza pista di scorrimento in vh (default: 420)")
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ERRORE: FFmpeg non trovato nel PATH di sistema.", file=sys.stderr)
        raise SystemExit(1)

    video_path = Path(args.video).resolve()
    if not video_path.is_file():
        print(f"ERRORE: File video non trovato: {video_path}", file=sys.stderr)
        raise SystemExit(1)

    out_root = Path(args.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    meta = probe_video(video_path)

    desktop_dir = out_root / "frames_desktop"
    desktop_files = extract_webp_sequence(
        ffmpeg=ffmpeg,
        video_path=video_path,
        out_folder=desktop_dir,
        fps=args.fps,
        max_width=args.desktop_width,
        quality=args.quality,
        max_frames=args.max_frames,
    )
    desktop_mb = folder_size_mb(desktop_files)

    mobile_files: list[Path] = []
    mobile_mb = 0.0
    if not args.no_mobile:
        mobile_dir = out_root / "frames_mobile"
        mobile_files = extract_webp_sequence(
            ffmpeg=ffmpeg,
            video_path=video_path,
            out_folder=mobile_dir,
            fps=args.fps,
            max_width=args.mobile_width,
            quality=max(65, args.quality - 6),
            max_frames=args.max_frames,
        )
        mobile_mb = folder_size_mb(mobile_files)

    warnings: list[str] = []
    if len(desktop_files) < 30:
        warnings.append("Meno di 30 fotogrammi estratti: lo scorrimento potrebbe risultare a scatti (usa un video di 4-6s a 24-30 fps).")
    if desktop_mb > 9.0:
        warnings.append(f"Sequenza desktop pesante ({desktop_mb} MB > 9 MB consigliati): abbassa --quality a 72 o --max-frames a 130.")
    if mobile_mb > 4.0:
        warnings.append(f"Sequenza mobile pesante ({mobile_mb} MB > 4 MB consigliati): abbassa --mobile-width a 720.")

    manifest = {
        "source_video": video_path.name,
        "source_meta": meta,
        "frame_count": len(desktop_files),
        "fps_extracted": args.fps,
        "desktop_total_mb": desktop_mb,
        "mobile_total_mb": mobile_mb,
        "desktop_frames": [f"frames_desktop/{f.name}" for f in desktop_files],
        "mobile_frames": [f"frames_mobile/{f.name}" for f in mobile_files],
        "warnings": warnings,
    }
    manifest_path = out_root / "frames.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.generate_html:
        html_path = out_root / "index.html"
        html_path.write_text(
            HTML_STARTER_TEMPLATE.format(title=args.title, scroll_vh=args.scroll_vh),
            encoding="utf-8",
        )

    print(json.dumps({
        "status": "ok",
        "output_dir": str(out_root),
        "frame_count": len(desktop_files),
        "desktop_total_mb": desktop_mb,
        "mobile_total_mb": mobile_mb,
        "html_generated": bool(args.generate_html),
        "warnings": warnings,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
