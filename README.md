<div align="center">
  <img src="static/hero-banner.svg" alt="Blooder — Libreria Aperta Skill, Strumenti &amp; Blooderskills" width="100%" />

  <br />

  <img src="https://img.shields.io/badge/Libreria_Skill-8_attive-ff1236?style=for-the-badge&labelColor=140407" alt="Skill attive" />
  <img src="https://img.shields.io/badge/Strumenti-1_attivi-ff1236?style=for-the-badge&labelColor=140407" alt="Strumenti attivi" />
  <img src="https://img.shields.io/badge/Blooderskills-0_moduli-10b981?style=for-the-badge&labelColor=140407" alt="Blooderskills" />
  <img src="https://img.shields.io/badge/Licenza-MIT-fbeef0?style=for-the-badge&labelColor=140407" alt="MIT License" />
  <img src="https://img.shields.io/badge/Python-3.10+-ff4d63?style=for-the-badge&labelColor=140407" alt="Python 3.10+" />
</div>

---

## Cos'è Blooder

**Blooder** è una libreria interattiva locale e open-source dal design **Red Matrix** progettata per raccogliere, filtrare e potenziare il meglio dell'ecosistema per **Agenti AI e sviluppo moderno**, senza dipendere da database cloud esterni o dipendenze pesanti.

L'architettura è divisa in **tre reparti complementari**:

1. **Libreria Skill** — Selezione ragionata delle migliori skill open-source per agenti AI, spiegate senza gergo inutile, con pro, contro onesti e risparmio reale.
2. **Strumenti** — Utility operative e CLI ad alto impatto per automatizzare desktop, API, sicurezza e mobile.
3. **Blooderskills** — Il laboratorio originale di **Blooder**: moduli specialistici verticali (*"il pezzo in più"*) costruiti per settore piattaforma (Fatturazione, Vendita, Guide, Automazione), collaudati sul campo ed esportati automaticamente in [`skills/`](skills/) per l'installazione diretta.

---

## Blooderskills pubblicate (Moduli originali)

> Nessun modulo verticale ancora pubblicato in [`skills/`](skills/). Ogni nuova **Blooderskill** creata nell'interfaccia comparirà automaticamente in questa tabella e sarà installabile con:
> ```bash
> npx skills add raffaeleditullo-cloud/Blooder --skill <nome-skill>
> ```

---

## Libreria Skill (8 selezionate)

| Skill | Categoria | Cosa fa in una riga |
| :--- | :--- | :--- |
| **[Anatomy](https://github.com/wheresryan22/anatomy)** | `Guide & Documentazione` | Costruisce illustrazioni tecniche interattive e diagrammi animati (in SVG e WebGL) per far capire visivamente come funziona un sistema. |
| **[Teach](https://github.com/mattpocock/skills)** | `Guide & Documentazione` | Genera mini-lezioni HTML interattive e schede pratiche riassuntive per spiegare un concetto o una piattaforma un passo alla volta. |
| **[Marketing Psychology](https://github.com/coreyhaines31/marketingskills)** | `Marketing & Conversioni` | Applica oltre 70 modelli psicologici reali e playbook di conversione per far fidare gli utenti e migliorare landing page, prezzi e SEO. |
| **[Ruflo](https://github.com/ruvnet/ruflo)** | `Agenti AI & Automazione` | Coordinatore multi-agente con memoria condivisa per far lavorare più agenti AI insieme sullo stesso progetto. |
| **[xtool](https://github.com/xtool-org/xtool)** | `Mobile & iOS` | Compila, firma e installa vere app iPhone (iOS in Swift) direttamente da Windows o Linux, senza avere un Mac. |
| **[PentAGI](https://github.com/vxcontrol/pentagi)** | `Sicurezza & Audit` | Squadra autonoma di agenti per testare la sicurezza della tua app in un ambiente Docker isolato. |
| **[Reverse API Engineer](https://github.com/kalil0321/reverse-api-engineer)** | `Integrazioni & API` | Osserva il traffico di un sito web nel browser e genera automaticamente il codice pulito per collegarti ai suoi dati. |
| **[Agent-Reach](https://github.com/Panniantong/agent-reach)** | `Dati Web & Ricerca` | Dà ai tuoi agenti AI accesso gratuito a X/Twitter, Reddit, YouTube, GitHub e forum senza pagare API. |

---

## Strumenti Operativi (1 selezionati)

| Strumento | Categoria | Cosa fa in una riga |
| :--- | :--- | :--- |
| **[Agent Desktop](https://github.com/vercel-labs/agent-desktop)** | `Automazione Desktop` | Permette a Claude Code e agli agenti AI di usare i programmi del tuo PC leggendo pulsanti e campi direttamente dal sistema, senza muovere il mouse. |

---

## Avvio rapido in locale (Zero dipendenze esterne)

Blooder usa esclusivamente la libreria standard di **Python 3.10+** (`http.server` + `sqlite3`) con interfaccia **Red Matrix** e font locali inclusi.

```bash
git clone https://github.com/raffaeleditullo-cloud/Blooder.git
cd Blooder
python app.py
```

- Su Windows ti basta fare doppio click su **`avvia_blooder.bat`** (apre automaticamente `http://127.0.0.1:8765`).
- Per verificare il database, aggiornare il catalogo JSON/README, controllare l'assenza di chiavi segrete e sincronizzare GitHub in un colpo solo, usa **`salva_progetto.bat`**.

---

## Sicurezza & Privacy by Design

- **Zero telemetria e zero cloud:** tutto gira su `127.0.0.1` e salva in `blooder.db` + `backup_libreria.json`.
- **Scudo anti-segreti integrato:** prima di ogni salvataggio Git, `sync_libreria.py` analizza i file tracciati e blocca automaticamente il commit se rileva chiavi private o token API.

---

## Licenza

Distribuito sotto licenza **[MIT](LICENSE)** — Copyright (c) 2026 **Raffaele Di Tullo**.
Le skill e gli strumenti di terze parti catalogati nella *Libreria Skill* e negli *Strumenti* appartengono ai rispettivi autori e mantengono le licenze dei relativi repository ufficiali.
