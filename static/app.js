let allSkills = [];
let allBlooderskills = [];
let currentSection = 'skill';
let activeCategory = 'Tutte';
let activeToolCategory = 'Tutte';
let activeBsSector = 'Tutti';
let editingSlug = null;
let editingBsSlug = null;
let selectedBaseSkills = [];

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function ico(name) {
  return `<svg class="ico" aria-hidden="true"><use href="#i-${name}"/></svg>`;
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2600);
}

function itemsByKind(kind) {
  return allSkills.filter(s => (s.kind || 'skill') === kind);
}

function handleMainAction() {
  if (currentSection === 'blooderskill') {
    openBsModal();
  } else {
    openAddModal();
  }
}

function switchSection(kind) {
  if (kind === 'tool') currentSection = 'tool';
  else if (kind === 'blooderskill') currentSection = 'blooderskill';
  else currentSection = 'skill';

  document.getElementById('view-skill').classList.toggle('hidden', currentSection !== 'skill');
  document.getElementById('view-tool').classList.toggle('hidden', currentSection !== 'tool');
  document.getElementById('view-blooderskill').classList.toggle('hidden', currentSection !== 'blooderskill');

  document.getElementById('tab-skill').classList.toggle('active', currentSection === 'skill');
  document.getElementById('tab-tool').classList.toggle('active', currentSection === 'tool');
  document.getElementById('tab-blooderskill').classList.toggle('active', currentSection === 'blooderskill');

  const labels = {
    skill: 'Aggiungi skill',
    tool: 'Aggiungi strumento',
    blooderskill: 'Crea Blooderskill'
  };
  document.getElementById('btn-add-label').textContent = labels[currentSection];
}

async function loadSkills() {
  const [resSkills, resBs] = await Promise.all([
    fetch('/api/skills'),
    fetch('/api/blooderskills')
  ]);
  const dataSkills = await resSkills.json();
  const dataBs = await resBs.json();
  allSkills = dataSkills.skills || [];
  allBlooderskills = dataBs.blooderskills || [];

  renderCategories();
  renderLibrary();
  renderToolCategories();
  renderTools();
  renderBsSectors();
  renderBlooderskills();
}

function renderCategories() {
  const items = itemsByKind('skill');
  const cats = ['Tutte', ...new Set(items.map(s => s.category).filter(Boolean))];
  if (!cats.includes(activeCategory)) activeCategory = 'Tutte';
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

function renderToolCategories() {
  const items = itemsByKind('tool');
  const cats = ['Tutte', ...new Set(items.map(s => s.category).filter(Boolean))];
  if (!cats.includes(activeToolCategory)) activeToolCategory = 'Tutte';
  const box = document.getElementById('tools-category-pills');
  box.innerHTML = cats.map(c => `
    <button class="pill ${c === activeToolCategory ? 'active' : ''}" onclick="setToolCategory('${esc(c)}')">
      ${esc(c)}
    </button>
  `).join('');
}

function setToolCategory(cat) {
  activeToolCategory = cat;
  renderToolCategories();
  renderTools();
}

function renderBsSectors() {
  const sectors = ['Tutti', ...new Set(allBlooderskills.map(b => b.sector).filter(Boolean))];
  if (!sectors.includes(activeBsSector)) activeBsSector = 'Tutti';
  const box = document.getElementById('bs-sector-pills');
  box.innerHTML = sectors.map(s => `
    <button class="pill ${s === activeBsSector ? 'active' : ''}" onclick="setBsSector('${esc(s)}')">
      ${esc(s)}
    </button>
  `).join('');
}

function setBsSector(sec) {
  activeBsSector = sec;
  renderBsSectors();
  renderBlooderskills();
}

function renderCardsGrid(items, queryText, selectedCat, gridId, emptyMessage) {
  const q = (queryText || '').toLowerCase().trim();
  const filtered = items.filter(s => {
    if (selectedCat !== 'Tutte' && s.category !== selectedCat) return false;
    if (!q) return true;
    const hay = [
      s.name, s.category, s.tagline, s.simple_explanation,
      ...(s.compatible_apps || []), ...(s.tech_keywords || [])
    ].join(' ').toLowerCase();
    return hay.includes(q);
  });

  const grid = document.getElementById(gridId);
  if (!filtered.length) {
    grid.innerHTML = `<div class="section-block empty">${emptyMessage}</div>`;
    return;
  }

  grid.innerHTML = filtered.map((s, i) => {
    const specs = s.specs || {};
    const meta = specs.linguaggio || specs.costo || '';
    return `
      <article class="skill-card" tabindex="0" role="button" aria-label="Apri la scheda di ${esc(s.name)}"
        onclick="openDetail(${s.id})"
        onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openDetail(${s.id}); }">
        <span class="card-index" aria-hidden="true">${String(i + 1).padStart(2, '0')}</span>
        <span class="badge">${esc(s.category)}</span>
        <h3 class="skill-title">${esc(s.name)}</h3>
        <p class="skill-tagline">${esc(s.tagline)}</p>
        <div class="card-foot">
          <span class="card-meta">${meta ? `${ico('code')} <span>${esc(meta)}</span>` : ''}</span>
          <span class="card-go" aria-hidden="true">${ico('arrow-right')}</span>
        </div>
      </article>
    `;
  }).join('');
}

function renderLibrary() {
  renderCardsGrid(
    itemsByKind('skill'),
    document.getElementById('search-input').value,
    activeCategory,
    'skills-grid',
    'Nessuna skill trovata. Clicca su <strong>Aggiungi skill</strong> per salvarne una nuova!'
  );
}

function renderTools() {
  renderCardsGrid(
    itemsByKind('tool'),
    document.getElementById('tools-search-input').value,
    activeToolCategory,
    'tools-grid',
    'Nessuno strumento trovato. Clicca su <strong>Aggiungi strumento</strong> per salvarne uno nuovo!'
  );
}

function renderBlooderskills() {
  const q = (document.getElementById('bs-search-input').value || '').toLowerCase().trim();
  const filtered = allBlooderskills.filter(b => {
    if (activeBsSector !== 'Tutti' && b.sector !== activeBsSector) return false;
    if (!q) return true;
    const hay = [
      b.name, b.sector, b.tagline, b.missing_piece,
      ...(b.base_skills || []), ...(b.use_cases || [])
    ].join(' ').toLowerCase();
    return hay.includes(q);
  });

  const grid = document.getElementById('bs-grid');
  if (!filtered.length) {
    grid.innerHTML = `
      <div class="section-block empty">
        Nessuna Blooderskill ancora pubblicata in questo filtro.<br/>
        Testiamo insieme i pezzi mancanti in chat e clicca su <strong>Crea Blooderskill</strong> per salvarli e pubblicarli a tuo nome!
      </div>
    `;
    return;
  }

  grid.innerHTML = filtered.map((b, i) => {
    const isReady = b.status === 'collaudata';
    const baseText = (b.base_skills && b.base_skills.length)
      ? `Potenzia: ${b.base_skills.join(', ')}`
      : 'Modulo originale Blooder';
    return `
      <article class="skill-card" tabindex="0" role="button" aria-label="Apri Blooderskill ${esc(b.name)}"
        onclick="openBsDetail(${b.id})"
        onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openBsDetail(${b.id}); }">
        <span class="card-index" aria-hidden="true">${String(i + 1).padStart(2, '0')}</span>
        <div class="badge-row">
          <span class="badge">${esc(b.sector)}</span>
          <span class="badge ${isReady ? 'badge-ready' : 'badge-draft'}">${isReady ? 'Collaudata' : 'In test'}</span>
        </div>
        <h3 class="skill-title">${esc(b.name)}</h3>
        <p class="skill-tagline">${esc(b.tagline)}</p>
        <div class="card-foot">
          <span class="card-meta">${ico('layers')} <span>${esc(baseText)}</span></span>
          <span class="card-go" aria-hidden="true">${ico('arrow-right')}</span>
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
  const compat = s.compatible_apps || [];
  const specRows = Object.entries(specs)
    .map(([k, v]) => `<li><strong>${esc(k.replace(/_/g, ' '))}</strong><span>${esc(v)}</span></li>`).join('');
  const box = document.getElementById('detail-content');
  box.innerHTML = `
    <div class="modal-header">
      <div>
        <span class="badge">${esc(s.category)}</span>
        <h2>${esc(s.name)}</h2>
        <p class="modal-sub">${esc(s.tagline)}</p>
      </div>
      <div class="modal-actions">
        <button class="btn btn-icon" onclick="closeModal('detail-modal'); openEditModal(${s.id})" title="Modifica" aria-label="Modifica">${ico('pencil')}</button>
        <button class="btn btn-icon" onclick="closeModal('detail-modal')" title="Chiudi" aria-label="Chiudi">${ico('x')}</button>
      </div>
    </div>

    <div class="steps" data-steps>
      <div class="steps-nav">
        <button class="step-tab" data-go="0"><b>1</b><span>Cos'è</span></button>
        <button class="step-tab" data-go="1"><b>2</b><span>Conviene?</span></button>
        <button class="step-tab" data-go="2"><b>3</b><span>Come si usa</span></button>
      </div>

      <div class="step-panel">
        <p class="lead">${esc(s.simple_explanation)}</p>
        ${compat.length ? `
          <div class="mini-label">Va bene per</div>
          <div class="chips">${compat.map(c => `<span class="chip">${esc(c)}</span>`).join('')}</div>
        ` : ''}
      </div>

      <div class="step-panel">
        <div class="duo">
          <div class="panel panel-blood">
            <h4>${ico('coin')} Ci guadagni</h4>
            <p>${esc(s.cost_saving || 'Soluzione gratuita open-source.')}</p>
          </div>
          <div class="panel">
            <h4>${ico('scale')} Da sapere prima</h4>
            <p>${esc(s.honest_tradeoffs || 'Nessun limite particolare segnalato.')}</p>
          </div>
        </div>
      </div>

      <div class="step-panel">
        <div class="panel">
          <div class="panel-head">
            <h4>${ico('wrench')} Installazione</h4>
            <button class="btn btn-sm" onclick="copyTextById('detail-guide', 'Guida copiata!')">${ico('copy')} Copia</button>
          </div>
          <pre class="code-box" id="detail-guide">${esc(s.install_guide || s.repo_url)}</pre>
        </div>
        ${specRows ? `
          <details class="more">
            <summary>Specifiche tecniche ${ico('chevron')}</summary>
            <div class="more-body"><ul class="kv">${specRows}</ul></div>
          </details>
        ` : ''}
        <div class="danger-row">
          <button class="btn btn-sm btn-danger" onclick="removeSkill(${s.id})">${ico('trash')} ${s.kind === 'tool' ? 'Elimina dagli strumenti' : 'Elimina dalla libreria'}</button>
        </div>
      </div>

      <div class="steps-foot">
        <button class="btn" data-prev>${ico('arrow-left')} Indietro</button>
        <span class="spacer"></span>
        <button class="btn" onclick="copyFormattedCard(${s.id})">${ico('copy')} Copia scheda</button>
        <button class="btn btn-primary" data-next>Avanti ${ico('arrow-right')}</button>
        <a class="btn btn-primary" data-last href="${esc(s.repo_url)}" target="_blank" rel="noopener">Apri su GitHub ${ico('external')}</a>
      </div>
    </div>
  `;
  initSteps(box);
  document.getElementById('detail-modal').classList.add('open');
}

function openBsDetail(id) {
  const b = allBlooderskills.find(x => x.id === id);
  if (!b) return;
  const isReady = b.status === 'collaudata';
  const bases = b.base_skills || [];
  const uses = b.use_cases || [];
  const box = document.getElementById('detail-content');

  box.innerHTML = `
    <div class="modal-header">
      <div>
        <div class="badge-row">
          <span class="badge">${esc(b.sector)}</span>
          <span class="badge ${isReady ? 'badge-ready' : 'badge-draft'}">${isReady ? 'Collaudata' : 'In test'}</span>
        </div>
        <h2>${esc(b.name)}</h2>
        <p class="modal-sub">${esc(b.tagline)}</p>
      </div>
      <div class="modal-actions">
        <button class="btn btn-icon" onclick="closeModal('detail-modal'); openEditBsModal(${b.id})" title="Modifica" aria-label="Modifica">${ico('pencil')}</button>
        <button class="btn btn-icon" onclick="closeModal('detail-modal')" title="Chiudi" aria-label="Chiudi">${ico('x')}</button>
      </div>
    </div>

    <div class="steps" data-steps>
      <div class="steps-nav">
        <button class="step-tab" data-go="0"><b>1</b><span>Il pezzo in più</span></button>
        <button class="step-tab" data-go="1"><b>2</b><span>SKILL.md</span></button>
        <button class="step-tab" data-go="2"><b>3</b><span>Usa a tuo nome</span></button>
      </div>

      <div class="step-panel">
        <div class="panel panel-blood">
          <h4>${ico('layers')} Cosa aggiunge che mancava</h4>
          <p>${esc(b.missing_piece)}</p>
        </div>
        ${bases.length ? `
          <div class="mini-label">Potenzia queste skill della libreria</div>
          <div class="chips">${bases.map(n => `<span class="chip">${esc(n)}</span>`).join('')}</div>
        ` : ''}
        ${uses.length ? `
          <div class="mini-label">Dove si usa nel settore ${esc(b.sector)}</div>
          <div class="chips">${uses.map(u => `<span class="chip">${esc(u)}</span>`).join('')}</div>
        ` : ''}
      </div>

      <div class="step-panel">
        <div class="panel">
          <div class="panel-head">
            <h4>${ico('code')} Contenuto completo (${esc(b.skill_path)})</h4>
            <button class="btn btn-sm" onclick="copyTextById('bs-detail-md', 'SKILL.md copiato negli appunti!')">${ico('copy')} Copia SKILL.md</button>
          </div>
          <pre class="code-box" id="bs-detail-md">${esc(b.skill_markdown)}</pre>
        </div>
      </div>

      <div class="step-panel">
        <div class="panel panel-blood">
          <div class="panel-head">
            <h4>${ico('zap')} Comando firmato a tuo nome</h4>
            <button class="btn btn-sm" onclick="copyTextById('bs-detail-cmd', 'Comando copiato!')">${ico('copy')} Copia comando</button>
          </div>
          <pre class="code-box" id="bs-detail-cmd">${esc(b.install_cmd)}</pre>
        </div>
        <div class="panel">
          <h4>${ico('folder')} Percorso nella libreria pubblica</h4>
          <p>Salvata automaticamente in <code>${esc(b.skill_path)}</code>. Quando avvii <code>salva_progetto.bat</code> viene aggiornata su GitHub.</p>
        </div>
        <div class="danger-row">
          <button class="btn btn-sm btn-danger" onclick="removeBlooderskill(${b.id})">${ico('trash')} Elimina da Blooderskills</button>
        </div>
      </div>

      <div class="steps-foot">
        <button class="btn" data-prev>${ico('arrow-left')} Indietro</button>
        <span class="spacer"></span>
        <button class="btn" onclick="copyBsCard(${b.id})">${ico('copy')} Copia pacchetto</button>
        <button class="btn btn-primary" data-next>Avanti ${ico('arrow-right')}</button>
        <a class="btn btn-primary" data-last href="${esc(b.repo_url)}" target="_blank" rel="noopener">Vedi su GitHub ${ico('external')}</a>
      </div>
    </div>
  `;
  initSteps(box);
  document.getElementById('detail-modal').classList.add('open');
}

async function copyBsCard(id) {
  const b = allBlooderskills.find(x => x.id === id);
  if (!b) return;
  const text = [
    `🩸 BLOODERSKILL: ${b.name.toUpperCase()} (${b.sector})`,
    `Comando installazione: ${b.install_cmd}`,
    b.base_skills?.length ? `Potenzia: ${b.base_skills.join(', ')}` : '',
    ``,
    `IL PEZZO IN PIÙ:`,
    b.missing_piece,
    ``,
    `--- FILE SKILL.md ---`,
    b.skill_markdown
  ].filter(Boolean).join('\n');
  await navigator.clipboard.writeText(text);
  showToast(`Blooderskill "${b.name}" copiata! Pronta da girare o incollare.`);
}

function renderBaseSkillChips() {
  const box = document.getElementById('bs-base-chips');
  if (!allSkills.length) {
    box.innerHTML = '<span class="hint">Nessuna skill base ancora presente.</span>';
    return;
  }
  box.innerHTML = allSkills.map(s => {
    const active = selectedBaseSkills.includes(s.name);
    return `
      <button type="button" class="chip chip-btn ${active ? 'selected' : ''}" onclick="toggleBaseSkill('${esc(s.name)}')">
        ${esc(s.name)}
      </button>
    `;
  }).join('');
}

function toggleBaseSkill(name) {
  if (selectedBaseSkills.includes(name)) {
    selectedBaseSkills = selectedBaseSkills.filter(n => n !== name);
  } else {
    selectedBaseSkills.push(name);
  }
  renderBaseSkillChips();
}

function openBsModal() {
  editingBsSlug = null;
  selectedBaseSkills = [];
  document.getElementById('bs-modal-title').textContent = 'Crea Blooderskill';
  setStep(document.getElementById('bs-steps'), 0);
  ['bs-name', 'bs-sector', 'bs-tagline', 'bs-missing', 'bs-usecases', 'bs-markdown']
    .forEach(id => { document.getElementById(id).value = ''; });
  document.getElementById('bs-status').value = 'collaudata';
  renderBaseSkillChips();
  document.getElementById('bs-modal').classList.add('open');
}

function openEditBsModal(id) {
  const b = allBlooderskills.find(x => x.id === id);
  if (!b) return;
  editingBsSlug = b.slug;
  selectedBaseSkills = [...(b.base_skills || [])];
  document.getElementById('bs-modal-title').textContent = `Modifica: ${b.name}`;
  setStep(document.getElementById('bs-steps'), 0);
  document.getElementById('bs-name').value = b.name || '';
  document.getElementById('bs-sector').value = b.sector || '';
  document.getElementById('bs-status').value = b.status === 'in_test' ? 'in_test' : 'collaudata';
  document.getElementById('bs-tagline').value = b.tagline || '';
  document.getElementById('bs-missing').value = b.missing_piece || '';
  document.getElementById('bs-usecases').value = (b.use_cases || []).join('\n');
  document.getElementById('bs-markdown').value = b.skill_markdown || '';
  renderBaseSkillChips();
  document.getElementById('bs-modal').classList.add('open');
}

function generateBsTemplate() {
  const name = document.getElementById('bs-name').value.trim() || 'Nuova Blooderskill';
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'blooderskill';
  const sector = document.getElementById('bs-sector').value.trim() || 'Generale';
  const tagline = document.getElementById('bs-tagline').value.trim() || name;
  const missing = document.getElementById('bs-missing').value.trim() || 'Descrivi qui il pezzo specialistico aggiunto.';
  const uses = document.getElementById('bs-usecases').value.split('\n').map(x => x.trim()).filter(Boolean);

  const lines = [
    '---',
    `name: ${slug}`,
    `description: "${tagline.replace(/"/g, "'")}"`,
    '---',
    '',
    `# ${name}`,
    '',
    `> **Settore piattaforma:** ${sector}`,
    selectedBaseSkills.length ? `> **Potenzia:** ${selectedBaseSkills.join(', ')}` : '> **Tipo:** Modulo originale Blooder',
    '',
    '## Obiettivo (Il pezzo in più)',
    missing,
    '',
    '## Regole operative per l\'Agente AI',
    '1. Analizza il contesto specifico del settore prima di generare codice o risposte.',
    '2. Applica controlli concreti, zero supposizioni e dati verificabili.',
    '3. Restituisci output chiari, azionabili e pronti per la produzione.',
    ''
  ];
  if (uses.length) {
    lines.push('## Casi d\'uso principali');
    uses.forEach(u => lines.push(`- ${u}`));
    lines.push('');
  }
  document.getElementById('bs-markdown').value = lines.join('\n');
  showToast('Struttura SKILL.md generata! Puoi rifinirla e pubblicare.');
}

async function saveBlooderskillForm() {
  const payload = {
    slug: editingBsSlug || undefined,
    name: document.getElementById('bs-name').value.trim(),
    sector: document.getElementById('bs-sector').value.trim() || 'Generale',
    status: document.getElementById('bs-status').value,
    base_skills: selectedBaseSkills,
    tagline: document.getElementById('bs-tagline').value.trim(),
    missing_piece: document.getElementById('bs-missing').value.trim(),
    use_cases: document.getElementById('bs-usecases').value.split('\n').map(x => x.trim()).filter(Boolean),
    skill_markdown: document.getElementById('bs-markdown').value.trim()
  };

  const res = await fetch('/api/blooderskills', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    showToast(data.error || 'Inserisci almeno il nome della Blooderskill.');
    return;
  }
  closeModal('bs-modal');
  switchSection('blooderskill');
  showToast(`Blooderskill "${data.name}" pubblicata ed esportata in ${data.skill_path}!`);
  await loadSkills();
}

async function removeBlooderskill(id) {
  if (!confirm('Vuoi davvero rimuovere questa Blooderskill da Blooder?')) return;
  await fetch(`/api/blooderskills/${id}`, { method: 'DELETE' });
  closeModal('detail-modal');
  showToast('Blooderskill rimossa.');
  await loadSkills();
}

function openAddModal() {
  editingSlug = null;
  const isTool = currentSection === 'tool';
  document.getElementById('form-modal-title').textContent = isTool ? 'Aggiungi strumento' : 'Aggiungi skill';
  document.getElementById('f-repo-label').textContent = isTool
    ? 'Incolla il link GitHub dello strumento'
    : 'Incolla il link GitHub della skill';
  setStep(document.getElementById('add-steps'), 0);
  ['f-repo', 'f-name', 'f-category', 'f-tagline', 'f-explanation', 'f-lang', 'f-os', 'f-compat', 'f-saving', 'f-tradeoffs', 'f-guide']
    .forEach(id => { document.getElementById(id).value = ''; });
  document.getElementById('f-kind').value = isTool ? 'tool' : 'skill';
  document.getElementById('f-os').value = 'Windows, macOS, Linux — 100% Gratuito';
  document.getElementById('add-modal').classList.add('open');
}

function openEditModal(id) {
  const s = allSkills.find(x => x.id === id);
  if (!s) return;
  editingSlug = s.slug;
  document.getElementById('form-modal-title').textContent = `Modifica: ${s.name}`;
  setStep(document.getElementById('add-steps'), 1);
  document.getElementById('f-repo').value = s.repo_url || '';
  document.getElementById('f-name').value = s.name || '';
  document.getElementById('f-kind').value = s.kind === 'tool' ? 'tool' : 'skill';
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
  btn.textContent = 'Lettura…';
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
    setStep(document.getElementById('add-steps'), 1);
  } catch (err) {
    showToast(err.message);
  } finally {
    btn.innerHTML = `${ico('zap')} Compila da GitHub`;
    btn.disabled = false;
  }
}

async function saveSkillForm() {
  const osRaw = document.getElementById('f-os').value.trim();
  const [osPart, costPart] = osRaw.split('—').map(x => x.trim());
  const selectedKind = document.getElementById('f-kind').value === 'tool' ? 'tool' : 'skill';
  const payload = {
    slug: editingSlug || undefined,
    kind: selectedKind,
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
  switchSection(selectedKind);
  showToast(
    selectedKind === 'tool'
      ? `Strumento "${data.name}" salvato in Strumenti!`
      : `Skill "${data.name}" salvata nella libreria!`
  );
  await loadSkills();
}

async function removeSkill(id) {
  const s = allSkills.find(x => x.id === id);
  const label = s && s.kind === 'tool' ? 'questo strumento' : 'questa skill';
  if (!confirm(`Vuoi davvero rimuovere ${label} da Blooder?`)) return;
  await fetch(`/api/skills/${id}`, { method: 'DELETE' });
  closeModal('detail-modal');
  showToast('Voce rimossa.');
  await loadSkills();
}

async function copyTextById(id, msg) {
  const txt = document.getElementById(id).textContent;
  await navigator.clipboard.writeText(txt);
  showToast(msg);
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

function closeOnBackdrop(e, id) {
  if (e.target.id === id) closeModal(id);
}

// --- Percorsi a 3 passi (solo navigazione tra pannelli, nessun dato) ---
function setStep(root, index) {
  if (!root) return;
  const panels = root.querySelectorAll(':scope > .step-panel');
  const tabs = root.querySelectorAll(':scope > .steps-nav .step-tab');
  const i = Math.max(0, Math.min(panels.length - 1, index));
  root.dataset.step = i;
  panels.forEach((p, n) => p.classList.toggle('active', n === i));
  tabs.forEach((t, n) => {
    t.classList.toggle('active', n === i);
    t.classList.toggle('done', n < i);
  });
  root.classList.toggle('is-first', i === 0);
  root.classList.toggle('is-last', i === panels.length - 1);
}

function initSteps(scope) {
  (scope || document).querySelectorAll('[data-steps]').forEach(r => setStep(r, 0));
}

document.addEventListener('click', e => {
  const btn = e.target.closest('[data-go], [data-next], [data-prev]');
  if (!btn) return;
  const root = btn.closest('[data-steps]');
  if (!root) return;
  const current = Number(root.dataset.step || 0);
  if (btn.hasAttribute('data-go')) setStep(root, Number(btn.dataset.go));
  else setStep(root, current + (btn.hasAttribute('data-next') ? 1 : -1));
});

initSteps();
loadSkills();
