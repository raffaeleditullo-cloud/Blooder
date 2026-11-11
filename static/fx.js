// Blooder — sfondo "pioggia di codice" rossa. Solo grafica: non tocca dati né funzioni.
(() => {
  const canvas = document.getElementById('bg-rain');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const GLYPHS = '01アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789ABCDEF<>/{}[]#$%&*+=';
  const SIZE = 16;
  let cols = 0, drops = [], speeds = [], w = 0, h = 0;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = window.innerWidth;
    h = window.innerHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#050002';
    ctx.fillRect(0, 0, w, h);
    cols = Math.ceil(w / SIZE);
    drops = Array.from({ length: cols }, () => Math.floor(Math.random() * -60));
    speeds = Array.from({ length: cols }, () => (Math.random() < 0.15 ? 2 : 1));
  }

  function glyph() {
    return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
  }

  function step() {
    ctx.fillStyle = 'rgba(5, 0, 2, 0.09)';
    ctx.fillRect(0, 0, w, h);
    ctx.font = `${SIZE}px Consolas, "Cascadia Mono", monospace`;
    ctx.textBaseline = 'top';
    for (let i = 0; i < cols; i++) {
      const x = i * SIZE;
      const y = drops[i] * SIZE;
      if (y > -SIZE) {
        // scia rosso sangue
        ctx.fillStyle = speeds[i] === 2 ? '#ff1236' : '#b3001f';
        ctx.fillText(glyph(), x, y - SIZE);
        // testa luminosa
        ctx.fillStyle = '#ffc9d0';
        ctx.fillText(glyph(), x, y);
      }
      drops[i] += speeds[i];
      if (y > h && Math.random() > 0.975) {
        drops[i] = Math.floor(Math.random() * -30);
        speeds[i] = Math.random() < 0.15 ? 2 : 1;
      }
    }
  }

  let last = 0;
  function loop(t) {
    if (!document.hidden && t - last > 55) {
      last = t;
      step();
    }
    requestAnimationFrame(loop);
  }

  resize();
  let rt;
  window.addEventListener('resize', () => {
    clearTimeout(rt);
    rt = setTimeout(() => {
      resize();
      if (reduce) for (let i = 0; i < 70; i++) step();
    }, 150);
  });

  if (reduce) {
    for (let i = 0; i < 70; i++) step(); // immagine fissa, nessuna animazione
  } else {
    requestAnimationFrame(loop);
  }
})();

// Riflesso rosso che segue il mouse sulle schede (solo grafica).
document.addEventListener('pointermove', e => {
  const card = e.target.closest && e.target.closest('.skill-card');
  if (!card) return;
  const r = card.getBoundingClientRect();
  card.style.setProperty('--mx', `${e.clientX - r.left}px`);
  card.style.setProperty('--my', `${e.clientY - r.top}px`);
});
