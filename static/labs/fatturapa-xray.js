/* ==========================================================
   BLOODER LAB — FatturaPA X-Ray (Motore Isometrico + Lezione)
   Costruito seguendo Anatomy (proiezione isometrica reale a 4 toni,
   ordine del pittore, moto smorzato esponenziale, telemetria vera)
   e Teach (4 missioni progressive con feedback immediato).
   Zero attributi CSS inline nei nodi DOM/SVG.
   ========================================================== */

const SVG_NS = 'http://www.w3.org/2000/svg';

// --- Stato globale del Laboratorio ---
const state = {
  mission: 0,
  doneMissions: new Set(),

  // Step 1: Scanner fatture fornitore
  activeSample: 0,
  docProgress: 0.15,
  docTarget: 0.42,
  needleDeg: -42,
  needleTarget: -38,
  scannerAlarm: 'ok', // 'ok' | 'err' | 'warn'

  // Step 2: Cancello SdI
  fixes: { dest: false, natura: false, bollo: false },
  gateLift: 0,
  gateTarget: 0,

  // Step 3: Calcolatore reale e serbatoi
  regime: 'forfettario',
  coeffAteco: 86,
  incasso: 3500,
  costiBase: 1400,
  rincaroPct: 0,

  // Livelli attuali (0..1) smorzati per i 3 serbatoi isometrici
  tankAmber: 0.35,
  tankAmberTarget: 0.35,
  tankRed: 0.28,
  tankRedTarget: 0.28,
  tankGreen: 0.32,
  tankGreenTarget: 0.32,

  outFornitori: 1400,
  outTasse: 1065,
  outNetto: 1035
};

// --- Proiezione Isometrica (Azimut 36°, Elevazione 30°) ---
const COS_A = Math.cos((34 * Math.PI) / 180);
const SIN_A = Math.sin((34 * Math.PI) / 180);
const ELEV = 0.54;
const ORIGIN_X = 274;
const ORIGIN_Y = 262;

function iso(x, y, z) {
  const sx = ORIGIN_X + (x - y) * COS_A;
  const sy = ORIGIN_Y + (x + y) * SIN_A * ELEV - z;
  return [Number(sx.toFixed(1)), Number(sy.toFixed(1))];
}

function pts(arr) {
  return arr.map(p => `${p[0]},${p[1]}`).join(' ');
}

function el(tag, attrs = {}, parent = null) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    node.setAttribute(k, String(v));
  }
  if (parent) parent.appendChild(node);
  return node;
}

// Disegna un parallelepipedo isometrico solido a 3 facce visibili (top, left +y, right +x)
function drawIsoBox(parent, x, y, z, w, d, h, tone = 'mid') {
  const g = el('g', {}, parent);
  const p001 = iso(x, y, z + h);
  const p101 = iso(x + w, y, z + h);
  const p111 = iso(x + w, y + d, z + h);
  const p011 = iso(x, y + d, z + h);

  const p010 = iso(x, y + d, z);
  const p110 = iso(x + w, y + d, z);
  const p100 = iso(x + w, y, z);

  // Faccia anteriore sinistra (y = y + d)
  el('polygon', { points: pts([p011, p111, p110, p010]), class: `iso-${tone}-left` }, g);
  // Faccia anteriore destra (x = x + w)
  el('polygon', { points: pts([p101, p111, p110, p100]), class: `iso-${tone}-right` }, g);
  // Faccia superiore (z = z + h)
  el('polygon', { points: pts([p001, p101, p111, p011]), class: `iso-${tone}-top` }, g);
  return g;
}

function updateLiquidPrism(faces, x, y, z, w, d, h) {
  const safeH = Math.max(2, h);
  const p001 = iso(x, y, z + safeH);
  const p101 = iso(x + w, y, z + safeH);
  const p111 = iso(x + w, y + d, z + safeH);
  const p011 = iso(x, y + d, z + safeH);
  const p010 = iso(x, y + d, z);
  const p110 = iso(x + w, y + d, z);
  const p100 = iso(x + w, y, z);

  faces.left.setAttribute('points', pts([p011, p111, p110, p010]));
  faces.right.setAttribute('points', pts([p101, p111, p110, p100]));
  faces.top.setAttribute('points', pts([p001, p101, p111, p011]));
}

// Riferimenti agli elementi dinamici SVG
const refs = {};

function buildMachineScene() {
  const svg = document.getElementById('iso-machine');
  svg.innerHTML = '';

  // 1. Ombra morbida a pavimento + Piedini in gomma (Back-to-front)
  const sh = [iso(-225, -88, -14), iso(225, -88, -14), iso(225, 92, -14), iso(-225, 92, -14)];
  el('polygon', { points: pts(sh), class: 'iso-shadow' }, svg);

  for (const [fx, fy] of [[-205, -72], [190, -72], [-205, 62], [190, 62]]) {
    drawIsoBox(svg, fx, fy, -12, 22, 22, 12, 'lo');
  }

  // 2. Piastra Base Pesante del Banco Ottico
  drawIsoBox(svg, -215, -82, 0, 435, 170, 16, 'lo');
  // Piastra superiore rialzata per nastro trasportatore (sinistra -> centro)
  drawIsoBox(svg, -200, -54, 16, 265, 112, 8, 'mid');

  // Viti agli angoli della piastra
  for (const [bx, by] of [[-204, -72], [208, -72], [-204, 76], [208, 76]]) {
    const [cx, cy] = iso(bx, by, 17);
    el('circle', { cx, cy, r: 3.2, class: 'iso-bolt' }, svg);
  }

  // Righello tecnico inciso sul bordo anteriore con tacche ogni 15 unità
  for (let rx = -195; rx <= 55; rx += 15) {
    const isMajor = rx % 45 === 0;
    const a = iso(rx, 58, 24.5);
    const b = iso(rx, isMajor ? 48 : 53, 24.5);
    el('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], class: 'iso-tick' }, svg);
  }

  // Binari gemelli del nastro di scorrimento fatture
  for (const ry of [-26, 26]) {
    const rStart = iso(-192, ry, 25);
    const rEnd = iso(58, ry, 25);
    el('line', { x1: rStart[0], y1: rStart[1], x2: rEnd[0], y2: rEnd[1], class: 'iso-rail' }, svg);
  }

  // 3. Montante posteriore del Portale Scanner Raggi-X (dietro al foglio!)
  drawIsoBox(svg, -108, -62, 24, 24, 18, 86, 'mid');

  //Montante posteriore Cancello Doganale SdI (dietro al foglio!)
  drawIsoBox(svg, 6, -62, 24, 20, 18, 76, 'mid');

  // 4. SLOT CENTRALE IN ORDINE DI PROFONDITÀ: Foglio Fattura XML Mobile
  refs.docGroup = el('g', {}, svg);
  buildInvoiceSheet(refs.docGroup);

  // 5. Fascio Laser Raggi-X + Traversa Superiore + Montante Anteriore Scanner
  const beamPts = [
    iso(-96, -46, 106),
    iso(-96, 46, 106),
    iso(-96, 46, 25),
    iso(-96, -46, 25)
  ];
  refs.laserBeam = el('polygon', { points: pts(beamPts), class: 'iso-lit-beam' }, svg);

  // Traversa ponte scanner
  drawIsoBox(svg, -112, -62, 108, 32, 128, 16, 'hi');
  // Montante anteriore scanner (davanti al foglio!)
  drawIsoBox(svg, -108, 48, 24, 24, 18, 86, 'hi');

  // Quadrante manometro analogico rincari sulla testa dello scanner
  const [gx, gy] = iso(-94, 67, 115);
  el('circle', { cx: gx, cy: gy - 18, r: 17, class: 'iso-lo-top' }, svg);
  el('circle', { cx: gx, cy: gy - 18, r: 13.5, class: 'iso-glass' }, svg);
  refs.needleGroup = el('g', { transform: `translate(${gx}, ${gy - 18}) rotate(-38)` }, svg);
  el('line', { x1: 0, y1: 2, x2: 0, y2: -11, class: 'iso-gate-bar' }, refs.needleGroup);
  el('circle', { cx: 0, cy: 0, r: 2.3, class: 'iso-led-ok' }, refs.needleGroup);

  // Spia luminosa sulla testa dello scanner
  const [lx, ly] = iso(-96, 0, 127);
  refs.scannerLed = el('circle', { cx: lx, cy: ly, r: 5.5, class: 'iso-led-ok' }, svg);
  const [stx, sty] = iso(-96, -15, 139);
  el('text', { x: stx - 24, y: sty, class: 'iso-svg-label' }, svg).textContent = '1·RAGGI-X';

  // 6. Stazione 2: Sbarra Dogana SdI (Mobile in altezza z) + Montante Anteriore
  refs.gateGroup = el('g', {}, svg);
  const bA = iso(16, -48, 44);
  const bB = iso(16, 48, 44);
  const bC = iso(16, 48, 34);
  const bD = iso(16, -48, 34);
  refs.gateBar = el('polygon', { points: pts([bA, bB, bC, bD]), class: 'iso-gate-bar' }, refs.gateGroup);

  // Montante anteriore SdI + scatola 3 spie errori
  drawIsoBox(svg, 6, 48, 24, 20, 20, 76, 'hi');
  refs.gateLeds = [];
  for (let i = 0; i < 3; i++) {
    const [sx, sy] = iso(27, 58, 48 + i * 16);
    refs.gateLeds.push(el('circle', { cx: sx, cy: sy, r: 4, class: 'iso-led-err' }, svg));
  }
  const [gtx, gty] = iso(16, -12, 114);
  el('text', { x: gtx - 20, y: gty, class: 'iso-svg-label' }, svg).textContent = '2·DOGANA SDI';

  // 7. Stazione 3: I 3 Serbatoi Separatori Soldi (Fornitori, Stato, Netto Tuo)
  // Ordine del pittore: dal fondo (-y) verso il fronte (+y)
  drawIsoBox(svg, 82, -68, 16, 122, 142, 8, 'mid');
  const tankSpecs = [
    { key: 'amber', y: -58, tagY: 162, dotClass: 'iso-led-warn', label: 'USCITE FORNITORI', fillClass: 'tank-fill-amber', valRef: 'lblAmber' },
    { key: 'red',   y: -10, tagY: 224, dotClass: 'iso-led-err',  label: 'SALVADANAIO STATO', fillClass: 'tank-fill-red',   valRef: 'lblRed' },
    { key: 'green', y:  38, tagY: 286, dotClass: 'iso-led-ok',   label: 'TASCA TUA (NETTO)', fillClass: 'tank-fill-green', valRef: 'lblGreen' }
  ];

  refs.tanks = {};
  for (const t of tankSpecs) {
    // Basamento serbatoio
    drawIsoBox(svg, 98, t.y, 24, 86, 34, 6, 'hi');
    // Liquido interno dinamico (3 facce aggiornate ogni frame)
    const liqG = el('g', {}, svg);
    const faces = {
      left: el('polygon', { class: t.fillClass }, liqG),
      right: el('polygon', { class: t.fillClass }, liqG),
      top: el('polygon', { class: t.fillClass }, liqG)
    };
    refs.tanks[t.key] = { y: t.y, faces };

    // Pareti di vetro esterne semitrasparenti sopra il liquido
    const gTop = [iso(100, t.y + 2, 118), iso(182, t.y + 2, 118), iso(182, t.y + 32, 118), iso(100, t.y + 32, 118)];
    const gLeft = [iso(100, t.y + 32, 118), iso(182, t.y + 32, 118), iso(182, t.y + 32, 30), iso(100, t.y + 32, 30)];
    const gRight = [iso(182, t.y + 2, 118), iso(182, t.y + 32, 118), iso(182, t.y + 32, 30), iso(182, t.y + 2, 30)];
    el('polygon', { points: pts(gLeft), class: 'iso-glass' }, svg);
    el('polygon', { points: pts(gRight), class: 'iso-glass' }, svg);
    el('polygon', { points: pts(gTop), class: 'iso-glass' }, svg);

    // Cavo telemetrico Anatomy con terminale sul bordo destro della vasca -> targhetta ordinata a destra
    const [portX, portY] = iso(182, t.y + 17, 86);
    const tagX = 492;
    const midX = tagX - 24;
    el('polyline', {
      points: `${portX},${portY} ${midX},${t.tagY + 21} ${tagX},${t.tagY + 21}`,
      class: 'iso-wire'
    }, svg);
    el('circle', { cx: portX, cy: portY, r: 3, class: t.dotClass }, svg);

    el('rect', { x: tagX, y: t.tagY, width: 168, height: 44, rx: 8, class: 'iso-tag-box' }, svg);
    el('circle', { cx: tagX + 13, cy: t.tagY + 15, r: 3.5, class: t.dotClass }, svg);
    el('text', { x: tagX + 23, y: t.tagY + 19, class: 'iso-svg-label' }, svg).textContent = t.label;
    refs[t.valRef] = el('text', { x: tagX + 23, y: t.tagY + 36, class: 'iso-svg-val' }, svg);
    refs[t.valRef].textContent = '0 €';
  }
}

function buildInvoiceSheet(group) {
  group.innerHTML = '';
  // Foglio adagiato a z=27 centrato attorno a x=0, poi traslato lungo il binario
  const sPts = [iso(-28, -20, 27), iso(28, -20, 27), iso(28, 20, 27), iso(-28, 20, 27)];
  el('polygon', { points: pts(sPts), class: 'iso-doc-sheet' }, group);

  // Righe inchiostro simulate sul foglio XML
  for (const ly of [-11, -3, 5, 12]) {
    const l1 = iso(-20, ly, 27.5);
    const l2 = iso(18, ly, 27.5);
    el('line', { x1: l1[0], y1: l1[1], x2: l2[0], y2: l2[1], class: 'iso-doc-ink' }, group);
  }
  const dot = iso(16, 5, 28);
  refs.docAlertDot = el('circle', { cx: dot[0], cy: dot[1], r: 4.2, class: 'iso-led-ok' }, group);
}

// --- Loop di Animazione Smorzata (Anatomy Exponential Follow) ---
function tickAnimation() {
  // Scorrimento carrello fattura lungo l'asse X isometrico (-165 -> +45)
  state.docProgress += (state.docTarget - state.docProgress) * 0.11;
  const worldX = -165 + state.docProgress * 210;
  const [base0x, base0y] = iso(0, 0, 0);
  const [currX, currY] = iso(worldX, 0, 0);
  if (refs.docGroup) {
    refs.docGroup.setAttribute(
      'transform',
      `translate(${(currX - base0x).toFixed(1)}, ${(currY - base0y).toFixed(1)})`
    );
  }

  // Ago manometro rincari
  state.needleDeg += (state.needleTarget - state.needleDeg) * 0.14;
  if (refs.needleGroup) {
    const [gx, gy] = iso(-94, 67, 115);
    refs.needleGroup.setAttribute(
      'transform',
      `translate(${gx}, ${gy - 18}) rotate(${state.needleDeg.toFixed(1)})`
    );
  }

  // Sollevamento sbarra SdI
  state.gateLift += (state.gateTarget - state.gateLift) * 0.14;
  if (refs.gateGroup) {
    refs.gateGroup.setAttribute('transform', `translate(0, ${(-state.gateLift).toFixed(1)})`);
  }

  // Livelli morbidi dei 3 serbatoi
  state.tankAmber += (state.tankAmberTarget - state.tankAmber) * 0.12;
  state.tankRed += (state.tankRedTarget - state.tankRed) * 0.12;
  state.tankGreen += (state.tankGreenTarget - state.tankGreen) * 0.12;

  if (refs.tanks) {
    updateLiquidPrism(refs.tanks.amber.faces, 102, refs.tanks.amber.y + 4, 30, 78, 26, state.tankAmber * 84);
    updateLiquidPrism(refs.tanks.red.faces, 102, refs.tanks.red.y + 4, 30, 78, 26, state.tankRed * 84);
    updateLiquidPrism(refs.tanks.green.faces, 102, refs.tanks.green.y + 4, 30, 78, 26, state.tankGreen * 84);
  }

  requestAnimationFrame(tickAnimation);
}

function fmtEuro(n) {
  const r = Math.round(n);
  const sign = r < 0 ? '-' : '';
  const abs = Math.abs(r).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${sign}${abs} €`;
}

// --- Navigazione tra i 4 Step (Teach) ---
function goMission(idx) {
  if (idx > state.mission) {
    state.doneMissions.add(state.mission);
  }
  state.mission = idx;

  document.querySelectorAll('.mission-tab').forEach((btn, i) => {
    btn.classList.toggle('active', i === idx);
    btn.classList.toggle('done', state.doneMissions.has(i));
  });
  document.querySelectorAll('.lesson-pane').forEach((pane, i) => {
    pane.classList.toggle('active', i === idx);
  });

  const figId = document.getElementById('plate-fig-id');
  const hint = document.getElementById('plate-hint');
  const readout = document.getElementById('plate-readout');

  if (idx === 0) {
    figId.textContent = 'FIG. 01 · STAZIONE RAGGI-X PREZZI';
    hint.textContent = 'Seleziona una fattura a destra per passarla sotto il laser.';
    const allFixed = state.fixes.dest && state.fixes.natura && state.fixes.bollo;
    state.gateTarget = allFixed ? 42 : 0;
    runScannerSample(state.activeSample);
  } else if (idx === 1) {
    figId.textContent = 'FIG. 02 · CANCELLO DOGANALE SDI';
    hint.textContent = 'Ripara i 3 interruttori a destra per alzare la sbarra dello Stato.';
    syncGateVisuals();
  } else if (idx === 2) {
    figId.textContent = 'FIG. 03 · SEPARATORE SOLDI VERI';
    hint.textContent = 'Trascina i cursori a destra: le 3 vasche reagiscono dal vivo.';
    state.docTarget = 1.02;
    state.gateTarget = 42;
    updateCalculator();
  } else {
    figId.textContent = 'FIG. 04 · BANCO COMPLETO ATTIVO';
    hint.textContent = 'Rispondi al quiz lampo o copia il comando pronto per usare la skill.';
    readout.textContent = 'SKILL PRONTA ALL\'USO';
    state.docTarget = 1.02;
    state.gateTarget = 42;
  }
}

// --- Logica Interattiva Passo 1: Scanner Rincari ---
function runScannerSample(sampleIdx) {
  state.activeSample = sampleIdx;
  [0, 1, 2].forEach(i => {
    document.getElementById(`sample-${i}`).classList.toggle('selected', i === sampleIdx);
  });

  // Riavvolge leggermente il foglio e lo fa scorrere sotto il laser (-96 corrisponde a ~0.33)
  state.docProgress = 0.04;
  state.docTarget = 0.35;

  const box = document.getElementById('step1-feedback');
  const readout = document.getElementById('plate-readout');

  if (sampleIdx === 0) {
    state.needleTarget = -36;
    refs.scannerLed.setAttribute('class', 'iso-led-ok');
    refs.docAlertDot.setAttribute('class', 'iso-led-ok');
    readout.textContent = 'CILINDRO: 28,50 € (BASE OK)';
    box.className = 'feedback-box state-ok';
    box.innerHTML = `
      <h4>Busta firmata .p7m aperta da sola!</h4>
      <p>Anche se il file aveva il lucchetto digitale (.p7m), la skill lo ha sbucciato e ha salvato in memoria il prezzo giusto: <strong>28,50 €</strong> a pezzo. Ora clicca sulla <strong>Fattura 2 (Marzo)</strong>!</p>
    `;
  } else if (sampleIdx === 1) {
    state.needleTarget = 48;
    refs.scannerLed.setAttribute('class', 'iso-led-err');
    refs.docAlertDot.setAttribute('class', 'iso-led-err');
    readout.textContent = 'ALLARME RINCARO: +18,95% (+76 €)';
    box.className = 'feedback-box state-err';
    box.innerHTML = `
      <h4>Beccato! Ti hanno sfilato 76,00 € in più senza avvisarti</h4>
      <p>In mezzo a tante righe normali, il cilindro è salito da 28,50 € a <strong>33,90 € (+54 €)</strong> e la schiuma da 5,80 € a <strong>6,90 € (+22 €)</strong>. A occhio nudo non lo vede nessuno, il laser lo becca in mezzo secondo!</p>
    `;
  } else {
    state.needleTarget = -12;
    refs.scannerLed.setAttribute('class', 'iso-led-warn');
    refs.docAlertDot.setAttribute('class', 'iso-led-warn');
    readout.textContent = 'NOTA CREDITO TD04: -82,72 € SOTTRATTI';
    box.className = 'feedback-box state-warn';
    box.innerHTML = `
      <h4>Trappola evitata: il rimborso viene tolto, non sommato!</h4>
      <p>Dentro il file XML della Nota di Credito (sigla <strong>TD04</strong>) c'è scritto "82,72" senza il segno meno. Un'IA normale lo sommerebbe alle tue spese: la nostra skill sa la legge italiana e <strong>toglie 82,72 €</strong> dai costi!</p>
    `;
  }
}

// --- Logica Interattiva Passo 2: Cancello SdI ---
function toggleGateFix(key) {
  state.fixes[key] = !state.fixes[key];
  syncGateVisuals();
}

function syncGateVisuals() {
  const items = [
    {
      key: 'dest',
      okText: 'Corretto a 7 caratteri esatti ("M5UXCR1") → Indirizzo valido!',
      errText: 'Scritto "ABC123" (6 lettere invece di 7) → Scarto immediato!'
    },
    {
      key: 'natura',
      okText: 'Inserita etichetta corretta "N2.2" (Regime Forfettario) → Valida!',
      errText: 'Lasciato vuoto o usato vecchio codice "N2" abolito → Bloccata!'
    },
    {
      key: 'bollo',
      okText: 'Aggiunto Bollo Virtuale da 2,00 € sopra 77,47 € → Zero multe!',
      errText: 'Fattura da 650 € senza IVA ma bollo dimenticato → Multa!'
    }
  ];

  let fixedCount = 0;
  items.forEach((item, idx) => {
    const isOk = state.fixes[item.key];
    if (isOk) fixedCount++;
    const btn = document.getElementById(`sw-${item.key}`);
    const desc = document.getElementById(`sw-${item.key}-desc`);
    const pill = document.getElementById(`sw-${item.key}-pill`);
    btn.classList.toggle('fixed', isOk);
    desc.textContent = isOk ? item.okText : item.errText;
    pill.textContent = isOk ? 'Riparato ✓' : 'Ripara';
    if (refs.gateLeds && refs.gateLeds[idx]) {
      refs.gateLeds[idx].setAttribute('class', isOk ? 'iso-led-ok' : 'iso-led-err');
    }
  });

  const box = document.getElementById('step2-feedback');
  const readout = document.getElementById('plate-readout');

  if (fixedCount === 3) {
    state.gateTarget = 42;
    state.docTarget = 0.96;
    refs.gateBar.setAttribute('class', 'iso-gate-bar-open');
    readout.textContent = 'DOGANA SDI: VIA LIBERA ✓';
    box.className = 'feedback-box state-ok';
    box.innerHTML = `
      <h4>Sbarra Alzata! Fattura promossa al 100%</h4>
      <p>Hai visto il foglio passare oltre il cancello? Ora il cliente riceve regolarmente la fattura e ti può pagare senza ritardi. Clicca su <strong>Apri il Calcolatore</strong> per vedere dove finiscono quei soldi!</p>
    `;
  } else {
    state.gateTarget = 0;
    state.docTarget = 0.72;
    refs.gateBar.setAttribute('class', 'iso-gate-bar');
    const rem = 3 - fixedCount;
    readout.textContent = `BLOCCATA: ${rem} ERRORI DA RIPARARE`;
    box.className = 'feedback-box state-err';
    box.innerHTML = `
      <h4>Sbarra Abbassata: mancano ancora ${rem} correzioni</h4>
      <p>Il foglio è fermo contro la sbarra rossa dello Stato. Clicca sui pulsanti "Ripara" rimasti rossi qui sopra per sbloccare il passaggio!</p>
    `;
  }
}

// --- Logica Interattiva Passo 3: Simulatore Calcolatore ---
function setRegime(reg) {
  state.regime = reg;
  document.getElementById('btn-reg-forf').classList.toggle('active', reg === 'forfettario');
  document.getElementById('btn-reg-ord').classList.toggle('active', reg === 'ordinario');
  document.getElementById('ateco-bar').classList.toggle('hidden', reg !== 'forfettario');
  updateCalculator();
}

function setAteco(coeff, btnEl) {
  state.coeffAteco = coeff;
  document.querySelectorAll('.ateco-chip').forEach(c => c.classList.remove('active'));
  btnEl.classList.add('active');
  updateCalculator();
}

function updateCalculator() {
  state.incasso = Number(document.getElementById('rng-incasso').value);
  state.costiBase = Number(document.getElementById('rng-costi').value);
  state.rincaroPct = Number(document.getElementById('rng-rincaro').value);

  document.getElementById('val-incasso').textContent = fmtEuro(state.incasso);
  document.getElementById('val-costi').textContent = fmtEuro(state.costiBase);
  document.getElementById('val-rincaro').textContent = `+${state.rincaroPct}%`;

  const extraRincaro = state.costiBase * (state.rincaroPct / 100);
  const costiEffettiviLordi = state.costiBase + extraRincaro;

  let tasseStato = 0;
  let nettoTasca = 0;

  if (state.regime === 'forfettario') {
    // Nel Forfettario l'IVA acquisti non si scarica e le tasse dipendono solo da Incasso * Coeff ATECO
    const imponibileForf = state.incasso * (state.coeffAteco / 100);
    const inps = imponibileForf * 0.24;
    const imposta = Math.max(0, imponibileForf - inps) * 0.15;
    tasseStato = inps + imposta;
    nettoTasca = state.incasso - costiEffettiviLordi - tasseStato;
  } else {
    // Ordinario semplificato: scorporiamo IVA 22% da incassi e costi
    const ricavoImponibile = state.incasso / 1.22;
    const ivaDebito = state.incasso - ricavoImponibile;
    const costoImponibile = costiEffettiviLordi / 1.22;
    const ivaCredito = costiEffettiviLordi - costoImponibile;
    const saldoIva = Math.max(0, ivaDebito - ivaCredito);
    const utile = Math.max(0, ricavoImponibile - costoImponibile);
    const irpefInps = utile * 0.38;
    tasseStato = saldoIva + irpefInps;
    nettoTasca = state.incasso - costiEffettiviLordi - tasseStato;
  }

  state.outFornitori = costiEffettiviLordi;
  state.outTasse = tasseStato;
  state.outNetto = nettoTasca;

  // Scala altezze serbatoi rispetto al massimo per far vedere chiaramente le proporzioni
  const scaleDenom = Math.max(state.incasso, costiEffettiviLordi + tasseStato, 1000);
  state.tankAmberTarget = Math.min(1, Math.max(0.04, costiEffettiviLordi / scaleDenom));
  state.tankRedTarget = Math.min(1, Math.max(0.04, tasseStato / scaleDenom));
  state.tankGreenTarget = nettoTasca <= 0 ? 0.03 : Math.min(1, nettoTasca / scaleDenom);

  document.getElementById('kpi-fornitori').textContent = fmtEuro(costiEffettiviLordi);
  document.getElementById('kpi-tasse').textContent = fmtEuro(tasseStato);
  document.getElementById('kpi-netto').textContent = fmtEuro(nettoTasca);

  if (refs.lblAmber) refs.lblAmber.textContent = fmtEuro(costiEffettiviLordi);
  if (refs.lblRed) refs.lblRed.textContent = fmtEuro(tasseStato);
  if (refs.lblGreen) refs.lblGreen.textContent = fmtEuro(nettoTasca);

  const readout = document.getElementById('plate-readout');
  readout.textContent = `NETTO VERO: ${fmtEuro(nettoTasca)}`;

  const fb = document.getElementById('step3-feedback');
  const title = document.getElementById('calc-insight-title');
  const body = document.getElementById('calc-insight-body');

  if (nettoTasca <= 0) {
    fb.className = 'feedback-box state-err';
    title.textContent = 'Allarme Rosso: stai lavorando in perdita!';
    body.textContent = 'Tra fornitori e tasse stai spendendo più di quello che incassi. Ecco perché scovare subito i rincari ed evitare prezzi troppo bassi ti salva l\'attività.';
  } else if (state.rincaroPct > 0) {
    fb.className = 'feedback-box state-warn';
    title.textContent = `Il rincaro nascosto del +${state.rincaroPct}% ti sta bruciando ${fmtEuro(extraRincaro)}!`;
    body.textContent = state.regime === 'forfettario'
      ? `Vedi il serbatoio verde? Nel Forfettario le tasse restano identiche (${fmtEuro(tasseStato)}), quindi tutti i ${fmtEuro(extraRincaro)} di rincaro escono dritti dalla tua tasca!`
      : `Anche in Regime Ordinario il rincaro gonfia la vasca fornitori e ti mangia liquidità vera sul conto corrente.`;
  } else {
    fb.className = 'feedback-box state-ok';
    title.textContent = 'Tutto sotto controllo: sai esattamente cosa puoi spendere';
    body.textContent = `Su ${fmtEuro(state.incasso)} incassati, metti subito da parte ${fmtEuro(tasseStato)} nel salvadanaio tasse: i restanti ${fmtEuro(nettoTasca)} sono puliti e davvero tuoi.`;
  }
}

// --- Logica Interattiva Passo 4: Quiz & Copia Comando ---
function answerQuiz(btn, isCorrect) {
  document.querySelectorAll('#quiz-box .quiz-opt').forEach(b => {
    b.classList.remove('correct', 'wrong');
  });
  btn.classList.add(isCorrect ? 'correct' : 'wrong');
  const fb = document.getElementById('quiz-feedback');
  if (isCorrect) {
    state.doneMissions.add(3);
    document.querySelectorAll('.mission-tab')[3].classList.add('done');
    fb.className = 'feedback-box state-ok';
    fb.innerHTML = `
      <h4>Esatto! Hai capito il cuore della skill meglio di un addetto ai lavori!</h4>
      <p>Nel file XML la Nota di Credito (TD04) non ha il segno meno davanti: senza FatturaPA X-Ray l'IA somma la spesa due volte invece di toglierla!</p>
    `;
  } else {
    fb.className = 'feedback-box state-err';
    fb.innerHTML = `
      <h4>Quasi! Riprova guardando la risposta centrale</h4>
      <p>Ricorda cosa è successo nello Step 1 quando abbiamo passato il reso merce (TD04) sotto il laser!</p>
    `;
  }
}

async function copyReadyPrompt() {
  const txt = [
    'npx skills add raffaeleditullo-cloud/Blooder --skill fatturapa-xray',
    '',
    '# Poi scrivi in chat al tuo agente AI:',
    '"Usa fatturapa-xray sulla mia cartella fatture XML: trovami rincari nascosti dei fornitori, eventuali errori SdI/bollo e calcola il mio netto vero tolte le tasse."'
  ].join('\n');
  await navigator.clipboard.writeText(txt);
  const t = document.getElementById('lab-toast');
  t.textContent = 'Comando + Prompt copiati negli appunti!';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2600);
}

// --- Avvio ---
buildMachineScene();
runScannerSample(0);
updateCalculator();
requestAnimationFrame(tickAnimation);
