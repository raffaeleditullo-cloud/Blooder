# Guida Operativa alle Skill Approvate — Blooder

Questa guida raccoglie le skill e i flussi approvati sul campo dopo test reali, indicando **come si attivano** e **dove danno il risultato migliore** (evitando gli errori tipici dell'AI).

---

## 1. Blender 3D (`blender-officina` + `blender-skills` + MCP)

* **Dove si trova:** `.agents/skills/blender-officina/SKILL.md` (ponte verso le 94 skill in `.agents/vendor_skills/blender-skills/`).
* **Prerequisito:** Blender aperto sul PC con l'add-on **MCP for Blender** connesso su porta `9876`.
* **Come si usa:** descrivi l'oggetto o la scena da costruire. L'agente deve seguire il percorso obbligatorio:
  1. `brief` (stile, dimensioni, uso finale)
  2. `clay pass` (geometria pulita senza materiali, verificata da più angolazioni con `look`)
  3. `materiali e luci` (studio lighting + shader)
  4. `render / export` (PNG, turntables o GLB).
* **Miglior utilizzo rilevato:**
  * Loghi 3D e icone brand (es. goccia Blooder 3D con smussi e riflessi reali).
  * Oggetti hero, diorami isometrici o stand da inserire nei Reel (`motionmaxxing` / `code-motion-studio`).
  * Modelli 3D riggati per giochi 2.5D/3D (dove l'animazione usa ossa vere e non deforma la mesh).

---

## 2. Gaming 2D & Effetti (`pixelfx` + Asset Pack Reali)

* **Dove si trova:** `.agents/vendor_skills/pixelfx/SKILL.md` (244 effetti procedurali MIT).
* **Lezione chiave dai test dal vivo:**
  * **Cosa NON fare:** non generare sprite sheet animate frame-by-frame con generatori di immagini AI per personaggi che camminano o combattono. Ogni frame cambia leggermente proporzioni e piedi, creando tremolio innaturale.
  * **Cosa funziona davvero:**
    1. Usa **asset pack 2D già animati da illustratori** (es. *Tiny Swords* di Pixel Frog o *Kenney.nl* CC0) per i personaggi (`Run`, `Attack`, `Idle`) e le torri.
    2. Usa l'AI (`image-generator`) solo per **elementi statici** (sfondi arena 16:9, illustrazioni carte, schermate titolo).
    3. Usa **`pixelfx`** per generare effetti particellari, esplosioni, colpi e level-up in codice (esportabili in GIF, PNG sprite sheet o Canvas).
* **Miglior utilizzo rilevato:** prototipi web HTML5 Canvas rapidi (stile *Clash of Skulls* / *Tiny Clash*) con 0 errori, animazioni fluide a 60fps e feedback visivo immediato.

---

## 3. Audio per Video-Guide & Reel (`sound-design` + `sfx/` + Kenney CC0)

* **Dove si trova:** `.agents/vendor_skills/sound-design/SKILL.md` (motore Python `sfx/` da `whaleyxbt/claude-motion` + 100 file `.ogg` CC0 in `kenney_interface_sounds/`).
* **Come si usa:**
  * Verifica i generatori disponibili: `python -m sfx --list` (eseguito dalla cartella `.agents/vendor_skills/sound-design/`).
  * Scrivi un cue sheet (`sfx/cues/<video>.py`) che legge lo stesso `timeline.json` del video, piazza `whoosh`, `pop`, `click`, `riser`, `impact`, `chime` e `pad` con stereo pan e ducking sotto la voce.
  * Renderizza il WAV già masterizzato automaticamente a **-14 LUFS** (standard YouTube/Instagram Reels).
* **Miglior utilizzo rilevato:** video-guide, demo prodotto e Reel generati con `motionmaxxing` o `code-motion-studio`, che altrimenti risultano muti o con volumi sbilanciati.

---

## 4. Scraping & Estrazione Dati Gratis (`scrapling-official` + `reverse-api-engineer`)

* **Dove si trova:** `.agents/vendor_skills/scrapling/SKILL.md` + `.agents/vendor_skills/reverse-api-engineer/SKILL.md`.
* **Come si usano in coppia (alternativa gratuita a Firecrawl):**
  1. Se il sito carica i dati tramite chiamate JSON nascoste -> usa **`reverse-api-engineer`** per intercettare il traffico e generare un client Python/TypeScript pulito.
  2. Se i dati sono dentro l'HTML o su pagine dinamiche -> usa **`Scrapling`** in Python (`pip install scrapling`) con selettori auto-healing (non si rompono al primo restyling CSS) e flag `--ai-targeted` da CLI.
  *(Per leggere singoli articoli, YouTube, X o GitHub resta prioritario `agent-reach`.)*
* **Miglior utilizzo rilevato:** monitoraggio listini/cataloghi, raccolta dati strutturati per automazioni PMI e sostituzione di servizi scraping a crediti.

---

## Skill Valutate e Scartate (Motivo)

* **Elephant-Goldfish Model (EGM):** scartato perché aggiunge complessità e consumo token pensato per spec enormi multi-team, inutile su progetti agili.
* **Seed Skill (11 startup skill):** scartato come doppione rispetto a `founder-board`, `founder-cfo`, `founder-offer`, `founder-pricing`, `founder-consumer` e `service-as-software-it` (che già coprono anche il fisco italiano).
* **ComfyUI Ref2VA VSA:** non installato (richiede ComfyUI locale con GPU di fascia alta tipo RTX 4090 24 GB).
* **77 Game Dev Skills:** tenuto fuori finché non si passa a motori completi (Godot 4, Unity, Unreal Engine 5).
