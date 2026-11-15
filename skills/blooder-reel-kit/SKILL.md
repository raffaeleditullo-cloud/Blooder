---
name: blooder-reel-kit
description: "Kit visivo 9:16 vettoriale Red Matrix con camera 3D continua, sottotitoli WordBoundary e suoni CC0 gratuiti da Openverse API."
---
# Blooder Reel Kit (9:16 Pro Pipeline)

Usa questa skill quando devi produrre un Reel verticale **1080x1920** in stile cyber-minimalist ad alta ritenzione senza scadere in slide statiche o screenshot sfocati.

## Componenti e Pipeline
1. **`openverse_sfx.py`**: ricerca e download gratuito di suoni `cc0` reali (whoosh, click, chime) da `https://api.openverse.org/v1/audio/` senza API key.
2. **Regia Audio-First (`edge-tts` + `WordBoundary`)**: genera prima la voce (`0` crediti) salvando `vo_timeline.json` con i timestamp parola-per-parola.
3. **Componenti Vettoriali Nitidi (zero `.png` zoomati)**:
   - Dial SVG a 24 tacche con `static/logo.svg`
   - Scheda Blooder Red Matrix vettoriale con pressione fisica su `Copia -> Copiato!`
   - Terminale `claude-code` con digitazione live
   - Righello frame-exact + forma d'onda guidata dall'ampiezza RMS reale di `vo_clean.wav`
   - Dock finale `[01][02][03]` + logo ufficiale `static/logo-full.svg`
4. **Collaudo obbligatorio (`look.py`)**: verifica `G0`, `G2`, `G3 PASS`, `0` tratti congelati `>= 0.6s` e ispezione di `sheet.jpg`.
