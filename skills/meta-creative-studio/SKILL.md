---
name: meta-creative-studio
description: "Trasforma un brief breve o vago in idee creative concrete, design avanzato con Claude (visual social 4:5 e 9:16, siti Lovable e WordPress con ui-ux-pro-max, 21st-dev, scroll-cinema-web e anatomy) e configurazione completa passo-passo di campagne Meta Ads con UTM e checklist pre-lancio."
---

# Meta & Design Creative Studio — Dal Brief Zero-File a Visual, Siti & Meta Ads

> **Modulo Originale Blooderskill** | Potenzia: `ui-ux-pro-max`, `21st-dev`, `scroll-cinema-web`, `anatomy`, `motionmaxxing`, `marketing-psychology`, `cro`, `sepia`

## 1. Sblocco Creativo dal Brief (Sempre 3 Angoli Diversi)
Quando parti solo da un brief (nessun file in ingresso) e manca l'idea, genera subito **3 concept completi**:
1. **Angolo 1 — Problema Reale (Stop-Scroll):** parte dal fastidio quotidiano del target.
2. **Angolo 2 — Risultato Concreto (Prima -> Dopo):** mostra cosa cambia in pratica.
3. **Angolo 3 — Prova / Offerta Diretta:** numeri, caso reale o invito chiaro all'azione.

Per ogni concept consegna:
- **Idea Visual + Testo in Grafica:** max 6-8 parole leggibili su mobile + prompt/layout visivo.
- **Hook + Body + CTA (stile `sepia`):** linguaggio umano, zero frasi fatte AI.
- **Formati da esportare:** Feed `1080x1350` (4:5), Stories/Reels `1080x1920` (9:16), Carosello `1080x1080` (1:1).

## 2. Design Avanzato con Claude (Visual & Siti di Livello)
Usa lo stack visivo di Blooder direttamente con Claude per superare i soliti template:
- **`ui-ux-pro-max` + `21st-dev`:** palette coerenti, tipografia forte, bento grid, card moderne e codice pronto da incollare in **Lovable** o **WordPress**.
- **`scroll-cinema-web`:** landing cinematografiche 60fps controllate dallo scroll.
- **`anatomy`:** diagrammi isometrici tecnici in SVG al posto delle solite icone stock.
- **`motionmaxxing` + `blooder-reel-kit`:** trasforma un visual statico in un Reel 9:16 animato.

## 3. Siti Web & Landing (Lovable & WordPress)
- **Lovable:** genera un Prompt Unico Strutturato (Hero sopra la piega -> Problema -> Soluzione -> Prove -> Offerta -> FAQ -> Form + pagina `/grazie` per evento Lead).
- **WordPress (Elementor / Gutenberg):** blueprint sezione per sezione + checklist tecnica (slug corto, Meta Title <=60ch, immagini WebP <200KB, test form reale, verifica mobile 375px).

## 4. Generatore Deterministico Piano Meta Ads (`scripts/meta_campaign_plan.py`)
```bash
python skills/meta-creative-studio/scripts/meta_campaign_plan.py --nome "Campagna Autunno" --obiettivo lead --budget-giornaliero 20 --giorni 14 --url "https://tuosito.it/offerta" --piattaforma-sito lovable
```
- Mai usare **Traffico** se vuoi contatti o vendite: scegli **Contatti (`lead`)** o **Vendite (`vendite`)**.
- Controlla sempre Localita, Pixel/Dataset, Evento di conversione e incolla gli **URL con UTM** generati dallo script.
