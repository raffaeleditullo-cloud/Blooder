---
name: scroll-cinema-web
description: "Costruisce siti web e landing page cinematografiche a 60fps controllate dallo scorrimento del mouse (stile Apple AirPods e studi automotive di lusso) partendo da due immagini AI e un video di transizione, estraendo sequenze leggere .webp con FFmpeg su HTML5 Canvas Retina. Usa questa skill ogni volta che devi progettare o programmare un sito scenografico ad altissimo impatto visivo senza modelli 3D WebGL pesanti."
---

# Scroll Cinema Web — Motore Siti Cinematografici su Canvas

> **Modulo Originale Blooderskill** | Potenzia: `motionmaxxing`, `Anatomy`, `Marketing Psychology`, `Sepia` | Zero dipendenze Python esterne + `FFmpeg`.

## Il Pezzo in Più (Perché i normali siti AI scattano)
Quando chiedi a un modello AI generico di fare un sito animato allo scroll usando un file `<video>` e cambiando `video.currentTime`, su Chrome e Safari mobile il sito **va a scatti** perché i codec MP4 comprimono i fotogrammi per differenze (*inter-frame*) e non riescono a riavvolgere fluidamente a 60fps.
**Scroll Cinema Web** risolve il problema alla radice con la stessa tecnica ingegneristica delle pagine prodotto Apple:
1. **Generazione AI furba senza modellazione 3D:** 2 sole immagini coerenti (*Start Frame* + *End Frame*) trasformate in un video fluido di `4–6 secondi` (con Veo 3, Kling o Runway);
2. **Taglio deterministico in `.webp` leggeri (`scripts/estrai_sequenza_webp.py`):** doppia sequenza automatica Desktop (`<= 1600px`) e Mobile (`<= 860px`) con controllo severo del peso in MB;
3. **Motore HTML5 `<canvas>` Retina a 60fps:** fisica morbida di scorrimento (*Lerp `0.12`*), caricamento progressivo istantaneo del primo frame, testi sincronizzati alle percentuali di scroll e rispetto automatico di `prefers-reduced-motion`.

---

## 1. Uso dello Script Deterministico (`scripts/estrai_sequenza_webp.py`)

Prima di scrivere la pagina web, converti **sempre** il video di transizione con lo script incluso nella skill:

```bash
# Estrae sequenza Desktop + Mobile, controlla il peso in MB e genera index.html + frames.json pronti
python skills/scroll-cinema-web/scripts/estrai_sequenza_webp.py "<percorso-video.mp4>" --out "./sito_cinema" --fps 24 --max-frames 150 --generate-html --title "Nome Brand"
```

### Regole Ferree di Peso e Fluidità (Controllate dallo Script)
- **Numero ideale di fotogrammi:** tra **`90` e `160` fotogrammi** (es. `5 secondi` a `24–30 fps`). Sotto i 30 frame sembra a scatti; sopra i 220 spreca RAM sui telefoni.
- **Budget massimo di peso:** **`< 9 MB`** totali su Desktop e **`< 4 MB`** totali su Smartphone (`frames_mobile/`). Se lo script segnala superamento soglia, rilancialo con `--quality 72` o `--max-frames 120`.

---

## 2. Le 4 Regole per Generare il Video Sorgente Perfetto (Veo 3 / Kling / Runway)
1. **Stessa lente e stessa scala tra Immagine A e Immagine B:** genera prima l'immagine iniziale (es. oggetto spento nel buio/fumo) e usa un riferimento visivo coerente per l'immagine finale (luci accese / dettaglio aperto) evitando salti assurdi di proporzioni.
2. **Un solo movimento di camera continuo:** chiedi nel prompt video *un lento dolly-in frontale o un'orbita morbida di 30 gradi*, **mai** tagli di montaggio o cambi scena bruschi a metà clip.
3. **Sfondo scuro o atmosferico consigliato:** fumo, controluce e superfici metalliche/lucide comprimono benissimo in `.webp` pesando la metà rispetto a prati o fogliame caotico, e fanno risaltare subito i titoli chiari in sovrimpressione.
4. **3 Battute di Testo al Massimo durante la Pista (`400vh`):**
   - `0% – 30%` scroll → Promessa forte + Bottone azione primario (`Marketing Psychology`);
   - `36% – 68%` scroll → Prova tecnica / beneficio concreto in 2 righe (`Sepia`);
   - `74% – 100%` scroll → Chiusura e invito diretto al contatto/prenotazione.
