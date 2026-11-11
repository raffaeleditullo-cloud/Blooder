let allSkills = [];
let activeCategory = 'Tutte';
let editingSlug = null;

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2600);
}

async function loadSkills() {
  const res = await fetch('/api/skills');
  const data = await res.json();
  allSkills = data.skills || [];
  renderCategories();
  renderLibrary();
}

function renderCategories() {
  const cats = ['Tutte', ...new Set(allSkills.map(s => s.category).filter(Boolean))];
  const box = document.getElementById('category-pills');
  box.innerHTML = cats.map(c => `
    <button class="pill ${c === activeCategory ? 'active' : ''}" onclick="setCategory('${esc(c)}')">
      ${esc(c)}
    </button>
  `).join('');
}

function setCategory(cat) {
  activeCategory = cat;
  renderCategories();
  renderLibrary();
}

function renderLibrary() {
  const q = (document.getElementById('search-input').value || '').toLowerCase().trim();
  const filtered = allSkills.filter(s => {
    if (activeCategory !== 'Tutte' && s.category !== activeCategory) return false;
    if (!q) return true;
    const hay = [
      s.name, s.category, s.tagline, s.simple_explanation,
      ...(s.compatible_apps || []), ...(s.tech_keywords || [])
    ].join(' ').toLowerCase();
    return hay.includes(q);
  });

  const grid = document.getElementById('skills-grid');
  if (!filtered.length) {
    grid.innerHTML = `<div class="section-block" style="grid-column: 1 / -1; text-align:center;">
      Nessuna skill trovata. Clicca su <strong>+ Aggiungi Skill</strong> in alto per salvarne una nuova!
    </div>`;
    return;
  }

  grid.innerHTML = filtered.map(s => {
    const specs = s.specs || {};
    const compat = (s.compatible_apps || []).slice(0, 3);
    return `
      <article class="skill-card">
        <div>
          <div class="card-top">
            <span class="badge">${esc(s.category)}</span>
            <a class="btn" style="padding: 4px 10px; font-size: 12px;" href="${esc(s.repo_url)}" target="_blank" rel="noopener">GitHub ↗</a>
          </div>
          <h3 class="skill-title">${esc(s.name)}</h3>
          <p class="skill-tagline">${esc(s.tagline)}</p>

          <div class="specs-mini">
            ${specs.linguaggio ? `<span class="spec-chip">💻 ${esc(specs.linguaggio)}</span>` : ''}
            ${specs.costo ? `<span class="spec-chip">🏷️ ${esc(specs.costo)}</span>` : ''}
          </div>

          <div style="margin-top: 12px;">
            <div style="font-size: 12px; font-weight: 700; color: var(--muted); margin-bottom: 4px; text-transform: uppercase;">
              App & Software compatibili:
            </div>
            <ul class="compat-list">
              ${compat.map(item => `<li>${esc(item)}</li>`).join('')}
            </ul>
          </div>
        </div>

        <div class="card-actions">
          <button class="btn btn-primary" onclick="openDetail(${s.id})">📖 Apri Scheda</button>
          <button class="btn" onclick="copyFormattedCard(${s.id})">📋 Copia per spiegare</button>
          <button class="btn" onclick="openEditModal(${s.id})" title="Modifica">✏️</button>
        </div>
      </article>
    `;
  }).join('');
}

function buildPlainTextCard(s) {
  const specs = s.specs || {};
  const specsLines = Object.entries(specs).map(([k, v]) => `- ${k.replace(/_/g, ' ')}: ${v}`).join('\n');
  const compatLines = (s.compatible_apps || []).map(c => `- ${c}`).join('\n');
  return [
    `🩸 ${s.name.toUpperCase()} (${s.category})`,
    `Link ufficiale: ${s.repo_url}`,
    ``,
    `COS'È IN PAROLE SEMPLICI:`,
    s.simple_explanation,
    ``,
    `SPECIFICHE TECNICHE:`,
    specsLines || '- Open Source',
    ``,
    `CON QUALI APP / SOFTWARE È COMPATIBILE:`,
    compatLines || '- Qualsiasi progetto compatibile',
    ``,
    `COSA TI FA RISPARMIARE:`,
    s.cost_saving || 'Gratuito',
    ``,
    `COMPROMESSO ONESTO DA SAPERE:`,
    s.honest_tradeoffs || 'Nessuna nota particolare.',
    ``,
    `COME SI USA / INSTALLA:`,
    s.install_guide || s.repo_url
  ].join('\n');
}

async function copyFormattedCard(id) {
  const s = allSkills.find(x => x.id === id);
  if (!s) return;
  await navigator.clipboard.writeText(buildPlainTextCard(s));
  showToast(`Scheda "${s.name}" copiata! Pronta da incollare ovunque.`);
}

function openDetail(id) {
  const s = allSkills.find(x => x.id === id);
  if (!s) return;
  const specs = s.specs || {};
  const box = document.getElementById('detail-content');
  box.innerHTML = `
    <div class="modal-header">
      <div>
        <span class="badge">${esc(s.category)}</span>
        <h2 style="margin-top: 6px;">${esc(s.name)}</h2>
      </div>
      <div style="display:flex; gap:8px;">
        <button class="btn btn-primary" onclick="copyFormattedCard(${s.id})">📋 Copia Tutta la Scheda</button>
        <button class="btn" onclick="closeModal('detail-modal')">✕</button>
      </div>
    </div>

    <div class="section-block">
      <h4>Cos'è (spiegato semplice per tutti)</h4>
      <div style="font-size: 14.5px;">${esc(s.simple_explanation)}</div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
      <div class="section-block">
        <h4>Specifiche Tecniche</h4>
        <ul class="compat-list">
          ${Object.entries(specs).map(([k, v]) => `<li><strong>${esc(k.replace(/_/g, ' '))}:</strong> ${esc(v)}</li>`).join('')}
        </ul>
      </div>
      <div class="section-block">
        <h4>App e Software Compatibili</h4>
        <ul class="compat-list">
          ${(s.compatible_apps || []).map(c => `<li>${esc(c)}</li>`).join('')}
        </ul>
      </div>
    </div>

    <div class="section-block box-green">
      <h4>💰 Vantaggio & Risparmio</h4>
      <div style="font-size: 13.5px;">${esc(s.cost_saving || 'Soluzione gratuita open-source.')}</div>
    </div>

    <div class="section-block box-amber">
      <h4>⚖️ Compromesso onesto (cosa sapere prima di usarla)</h4>
      <div style="font-size: 13.5px;">${esc(s.honest_tradeoffs || 'Nessun limite particolare segnalato.')}</div>
    </div>

    <div class="section-block">
      <h4>🛠️ Guida Pratica d'Installazione</h4>
      <pre class="code-box">${esc(s.install_guide)}</pre>
    </div>

    <div style="display:flex; justify-content:space-between; align-items:center; margin-top: 14px;">
      <a class="btn" href="${esc(s.repo_url)}" target="_blank" rel="noopener">🔗 Apri Repository GitHub</a>
      <button class="btn" style="color:#fda4af;" onclick="removeSkill(${s.id})">🗑️ Elimina dalla libreria</button>
    </div>
  `;
  document.getElementById('detail-modal').classList.add('open');
}

function openAddModal() {
  editingSlug = null;
  document.getElementById('form-modal-title').textContent = 'Aggiungi Skill alla Libreria';
  ['f-repo', 'f-name', 'f-category', 'f-tagline', 'f-explanation', 'f-lang', 'f-os', 'f-compat', 'f-saving', 'f-tradeoffs', 'f-guide']
    .forEach(id => { document.getElementById(id).value = ''; });
  document.getElementById('f-os').value = 'Windows, macOS, Linux — 100% Gratuito';
  document.getElementById('add-modal').classList.add('open');
}

function openEditModal(id) {
  const s = allSkills.find(x => x.id === id);
  if (!s) return;
  editingSlug = s.slug;
  document.getElementById('form-modal-title').textContent = `Modifica: ${s.name}`;
  document.getElementById('f-repo').value = s.repo_url || '';
  document.getElementById('f-name').value = s.name || '';
  document.getElementById('f-category').value = s.category || '';
  document.getElementById('f-tagline').value = s.tagline || '';
  document.getElementById('f-explanation').value = s.simple_explanation || '';
  document.getElementById('f-lang').value = (s.specs && s.specs.linguaggio) || '';
  document.getElementById('f-os').value = [s.specs?.sistemi_operativi, s.specs?.costo].filter(Boolean).join(' — ');
  document.getElementById('f-compat').value = (s.compatible_apps || []).join('\n');
  document.getElementById('f-saving').value = s.cost_saving || '';
  document.getElementById('f-tradeoffs').value = s.honest_tradeoffs || '';
  document.getElementById('f-guide').value = s.install_guide || '';
  document.getElementById('add-modal').classList.add('open');
}

async function autoFillFromGitHub() {
  const url = document.getElementById('f-repo').value.trim();
  if (!url) {
    showToast('Incolla prima un link GitHub!');
    return;
  }
  const btn = document.getElementById('btn-fetch-gh');
  btn.textContent = '⏳ Lettura...';
  btn.disabled = true;
  try {
    const res = await fetch('/api/github-preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_url: url })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Errore lettura GitHub');

    document.getElementById('f-name').value = data.name || '';
    document.getElementById('f-category').value = data.category || 'Nuova Skill';
    document.getElementById('f-tagline').value = data.tagline || '';
    document.getElementById('f-explanation').value = data.simple_explanation || '';
    document.getElementById('f-lang').value = data.specs?.linguaggio || '';
    document.getElementById('f-os').value = `${data.specs?.sistemi_operativi || 'Cross-platform'} — ${data.specs?.costo || 'Gratuito'}`;
    document.getElementById('f-compat').value = (data.compatible_apps || []).join('\n');
    document.getElementById('f-saving').value = data.cost_saving || '';
    document.getElementById('f-tradeoffs').value = data.honest_tradeoffs || '';
    document.getElementById('f-guide').value = data.install_guide || '';
    showToast('Dati importati da GitHub! Controlla e salva.');
  } catch (err) {
    showToast(err.message);
  } finally {
    btn.textContent = '⚡ Compila da GitHub';
    btn.disabled = false;
  }
}

async function saveSkillForm() {
  const osRaw = document.getElementById('f-os').value.trim();
  const [osPart, costPart] = osRaw.split('—').map(x => x.trim());
  const payload = {
    slug: editingSlug || undefined,
    repo_url: document.getElementById('f-repo').value.trim(),
    name: document.getElementById('f-name').value.trim(),
    category: document.getElementById('f-category').value.trim() || 'Generale',
    tagline: document.getElementById('f-tagline').value.trim(),
    simple_explanation: document.getElementById('f-explanation').value.trim(),
    specs: {
      linguaggio: document.getElementById('f-lang').value.trim() || 'Open Source',
      sistemi_operativi: osPart || 'Windows, macOS, Linux',
      costo: costPart || '100% Gratuito'
    },
    compatible_apps: document.getElementById('f-compat').value.split('\n').map(x => x.trim()).filter(Boolean),
    tech_keywords: document.getElementById('f-lang').value.toLowerCase().split(/[,\s/]+/).filter(Boolean),
    cost_saving: document.getElementById('f-saving').value.trim(),
    honest_tradeoffs: document.getElementById('f-tradeoffs').value.trim(),
    install_guide: document.getElementById('f-guide').value.trim()
  };

  const res = await fetch('/api/skills', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    showToast(data.error || 'Compila almeno Nome e Link GitHub.');
    return;
  }
  closeModal('add-modal');
  showToast(`Skill "${data.name}" salvata nella libreria!`);
  await loadSkills();
}

async function removeSkill(id) {
  if (!confirm('Vuoi davvero rimuovere questa skill dalla libreria Blooder?')) return;
  await fetch(`/api/skills/${id}`, { method: 'DELETE' });
  closeModal('detail-modal');
  showToast('Skill rimossa.');
  await loadSkills();
}

async function loadDecisions() {
  const res = await fetch('/api/decisions');
  const data = await res.json();
  const list = data.decisions || [];
  const box = document.getElementById('decisions-list');
  if (!list.length) {
    box.innerHTML = `<div class="section-block" style="text-align:center; color: var(--muted);">
      Nessuna scelta registrata per ora. Quando chiederai a Claude o ChatGPT di controllare una tua cartella progetto con Blooder e dirai "Approvo" o "Salta", la scelta comparirà qui!
    </div>`;
    return;
  }

  box.innerHTML = list.map(d => `
    <div class="decision-row">
      <div>
        <div style="font-size: 14.5px; font-weight: 700;">
          Progetto: <span style="color:#fda4af;">${esc(d.project_name)}</span> → Skill: ${esc(d.skill_name)}
        </div>
        <div style="font-size: 12.5px; color: var(--muted);">
          ${d.notes ? esc(d.notes) + ' • ' : ''}${new Date(d.decided_at).toLocaleString('it-IT')}
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:10px;">
        <span class="status-pill ${d.decision === 'approved' ? 'status-approved' : 'status-skipped'}">
          ${d.decision === 'approved' ? '✓ Approvata' : '⏭ Saltata (non verrà riproposta)'}
        </span>
        <button class="btn" style="padding: 5px 10px; font-size: 12px;" onclick="resetDecision(${d.id})">Ripristina</button>
      </div>
    </div>
  `).join('');
}

async function resetDecision(id) {
  await fetch(`/api/decisions/${id}`, { method: 'DELETE' });
  showToast('Scelta azzerata: la skill potrà essere valutata di nuovo.');
  await loadDecisions();
}

async function loadConnectorConfig() {
  const res = await fetch('/api/config-info');
  const info = await res.json();
  const mcpJson = {
    mcpServers: {
      blooder: {
        command: "python",
        args: [info.mcp_server_path]
      }
    }
  };
  document.getElementById('mcp-config-box').textContent = JSON.stringify(mcpJson, null, 2);
  document.getElementById('openapi-url-label').textContent = info.openapi_url;
}

async function copyTextById(id, msg) {
  const txt = document.getElementById(id).textContent;
  await navigator.clipboard.writeText(txt);
  showToast(msg);
}

function switchView(view) {
  ['library', 'decisions', 'connect'].forEach(v => {
    document.getElementById(`view-${v}`).classList.toggle('hidden', v !== view);
    document.getElementById(`tab-${v}`).classList.toggle('active', v === view);
  });
  if (view === 'decisions') loadDecisions();
  if (view === 'connect') loadConnectorConfig();
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

function closeOnBackdrop(e, id) {
  if (e.target.id === id) closeModal(id);
}

loadSkills();
