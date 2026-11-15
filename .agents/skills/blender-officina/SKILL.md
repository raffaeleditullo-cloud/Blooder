---
name: blender-officina
description: >-
  Ponte Blooder verso le 94 Blender Skills (arjun988/blender-skills) e MCP for Blender.
  Usare quando l'utente chiede di modellare, illuminare, renderizzare o animare qualcosa
  in Blender o in 3D (loghi 3D, oggetti per Reel, diorami isometrici, stand, asset per giochi).
  Impone il percorso brief -> riferimento -> clay pass -> materiali e luci -> QA.
---

# Blender Officina (ponte Blooder)

Le 94 skill complete stanno in `.agents/vendor_skills/blender-skills/.claude/skills/` (percorso `BS` qui sotto).
Non caricarle tutte: apri solo quelle indicate dal punto 2.

## 0. Prerequisiti (controlla prima di tutto)
1. Strumenti MCP `blender` disponibili: chiama `get_addon_status`, poi `get_scene_info`.
2. Se non risponde: in Blender premi N, scheda *MCP for Blender*, **Start MCP Server**.
   Se l'add-on è vecchio: `uvx mcp-for-blender install-addon`, poi disattiva e riattiva l'add-on.
3. Leggi `C:\Users\<utente>\.gemini\antigravity\mcp\blender\instructions.md` (regole sui nodi e sugli enum).

## 1. Brief (obbligatorio, prima di toccare Blender)
Scrivi una scheda di produzione con: tipo di asset, uso (Reel / slide / gioco), stile, budget triangoli
(`BS/references/polycount-budgets.md`), palette in hex, camera, luci, export.
Se c'è un riferimento (SVG, foto, schizzo) compila `BS/references/reference-analysis-template.md`
e misura la forma DAL riferimento: non a occhio.

## 2. Routing: quali skill aprire
| Richiesta | Apri |
|---|---|
| Qualsiasi asset | `BS/blender-director/SKILL.md` |
| Logo / oggetto da vetrina | `prop-artist`, `materials`, `lighting` (rig *Product Hero Shot*), `lookdev` |
| Diorama isometrico / slide | `isometric-style`, `camera-cinematography`, `lowpoly-style` |
| Stand, interni, uffici | `archviz`, `lighting`, `rendering` |
| Asset per gioco | `asset-optimization`, `export-pipeline`, `godot-export` / `unity-export` / `unreal-export` |
| Animazione breve per video | `animation`, `camera-cinematography`, `rendering` |
| Chiusura di ogni lavoro | `qa-review` + `BS/references/validation-checklist.md` |

## 3. Esecuzione (regole d'oro Blooder)
1. **Scena nuova** con nome dedicato; mai modificare la scena aperta dell'utente.
2. **Nomi univoci** con prefisso di progetto (`SM_Blooder_...`, `MAT_...`, `LGT_...`, `CAM_...`, `COL_...`).
   Prima di modificare un oggetto, recuperalo dal modificatore o dalla collezione della scena, non solo per nome:
   due scene possono avere oggetti omonimi.
3. **Clay pass grigio prima dei colori**, con camera 3/4 e camera ortografica frontale.
   Usa `look` o un render per vedere: è qui che emergono i bug di geometria.
4. Booleane: cutter **chiusi e senza auto-intersezioni** (verifica 0 spigoli non-manifold).
5. Una variabile per giro (materiale OPPURE luce OPPURE camera), massimo 3 giri.
6. EEVEE per i giri di prova, Cycles su GPU per il render finale.
7. Salva una copia `.blend` e i render in `_privato/blender_lab/` (fuori da GitHub).

## 4. QA finale (obbligatorio)
Riporta: triangoli contro budget, numero materiali, spigoli non-manifold, dimensioni, nomi,
render 3/4 + frontale, difetti per gravità (Blocker/Major/Minor/Note) e verdetto
**SHIP / SHIP WITH NOTES / NO-SHIP**.

## Sicurezza
`execute_blender_code` esegue Python nel Blender dell'utente: non aprire né importare file `.blend`
di provenienza sconosciuta con l'MCP attivo. `generate_3d` può consumare crediti: chiedi prima.
