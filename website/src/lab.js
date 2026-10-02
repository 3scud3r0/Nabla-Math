const TAU = Math.PI * 2;

export const FIELD_META = Object.freeze({
  orbit: {name: 'Potencial orbital', equation: '∇Φ = −r / ‖r‖³'},
  wave: {name: 'Interferência harmônica', equation: 'ψ = sin(k₁·r) + cos(k₂·r)'},
  chaos: {name: 'Atrator não linear', equation: 'ẋ = σ(y−x)'}
});

export function mulberry32(seed) {
  let state = seed >>> 0;
  return () => {
    state |= 0;
    state = state + 0x6d2b79f5 | 0;
    let value = Math.imul(state ^ state >>> 15, 1 | state);
    value = value + Math.imul(value ^ value >>> 7, 61 | value) ^ value;
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };
}

export function fieldVector(mode, x, y, time = 0) {
  if (mode === 'wave') return {x: Math.sin(y * 3.1 + time) * .62 + Math.cos(x * 2.2 - time * .4) * .22, y: Math.cos(x * 2.7 - time * .8) * .62 - Math.sin(y * 2.4 + time * .3) * .22};
  if (mode === 'chaos') return {x: Math.sin(y * 2.4 + time * .7) - x * .32 + y * .18, y: Math.sin(x * 3.2 - time * .5) - y * .3 - x * .16};
  if (x === 0 && y === 0) return {x: 0, y: 0};
  const radius2 = x * x + y * y + .055;
  const force = .18 / Math.pow(radius2, 1.5);
  return {x: -x * force - y * .48, y: -y * force + x * .48};
}

function setupLab() {
  const canvas = document.getElementById('field-canvas');
  if (!canvas) return;
  const context = canvas.getContext('2d', {alpha: false});
  if (!context) return;
  const section = canvas.closest('.lab');
  const modes = [...section.querySelectorAll('.lab-mode')];
  const pause = document.getElementById('field-pause');
  const name = document.getElementById('field-name');
  const equation = document.getElementById('field-equation');
  const energy = document.getElementById('field-energy');
  const particleLabel = document.getElementById('field-particles');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const random = mulberry32(0x4e41424c);
  const pointer = {x: 0, y: 0, active: false};
  let width = 1, height = 1, mode = 'orbit', paused = reducedMotion, animationId = 0, last = 0, clock = 0, particles = [];

  function resetParticle(particle, initial = false) {
    const angle = random() * TAU;
    const radius = (.13 + random() * .88) * Math.min(width, height) * .58;
    Object.assign(particle, {x: width * .64 + Math.cos(angle) * radius * 1.35, y: height * .5 + Math.sin(angle) * radius, vx: (random() - .5) * (initial ? .25 : .08), vy: (random() - .5) * (initial ? .25 : .08), life: 240 + random() * 520, hue: 148 + random() * 52});
    particle.px = particle.x; particle.py = particle.y;
    return particle;
  }
  function seedParticles() {
    const count = Math.max(360, Math.min(1200, Math.round(width * height / 850)));
    particles = Array.from({length: count}, () => resetParticle({}, true));
    particleLabel.textContent = count.toLocaleString('pt-BR');
  }
  function resize() {
    const rect = section.getBoundingClientRect();
    const ratio = Math.min(devicePixelRatio || 1, 2);
    width = Math.max(1, rect.width); height = Math.max(620, rect.height);
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
    canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    seedParticles(); context.fillStyle = '#05080d'; context.fillRect(0, 0, width, height);
  }
  function draw(timestamp) {
    const dt = Math.min(2, (timestamp - last) / 16.67 || 1); last = timestamp; clock += .008 * dt;
    context.fillStyle = 'rgba(5, 8, 13, .105)'; context.fillRect(0, 0, width, height);
    context.globalCompositeOperation = 'lighter'; let totalEnergy = 0;
    for (const particle of particles) {
      particle.px = particle.x; particle.py = particle.y;
      const vector = fieldVector(mode, (particle.x - width * .64) / Math.min(width, height), (particle.y - height * .5) / Math.min(width, height), clock);
      particle.vx = particle.vx * .965 + vector.x * dt * .37; particle.vy = particle.vy * .965 + vector.y * dt * .37;
      if (pointer.active) { const dx = pointer.x - particle.x, dy = pointer.y - particle.y, pull = Math.min(1.4, 5200 / (dx * dx + dy * dy + 900)); particle.vx += dx * pull * .0035; particle.vy += dy * pull * .0035; }
      const speed = Math.hypot(particle.vx, particle.vy), cap = 3.2;
      if (speed > cap) { particle.vx *= cap / speed; particle.vy *= cap / speed; }
      particle.x += particle.vx * dt; particle.y += particle.vy * dt; particle.life -= dt; totalEnergy += Math.min(speed, cap) / cap;
      if (particle.life < 0 || particle.x < -30 || particle.x > width + 30 || particle.y < -30 || particle.y > height + 30) resetParticle(particle);
      context.beginPath(); context.moveTo(particle.px, particle.py); context.lineTo(particle.x, particle.y);
      context.strokeStyle = `hsla(${particle.hue}, 76%, 67%, ${.12 + speed * .14})`; context.lineWidth = .45 + Math.min(speed, 2) * .35; context.stroke();
    }
    context.globalCompositeOperation = 'source-over'; energy.textContent = (totalEnergy / particles.length).toFixed(3);
    if (!paused) animationId = requestAnimationFrame(draw);
  }
  function setMode(nextMode) {
    if (!FIELD_META[nextMode]) return;
    mode = nextMode; name.textContent = FIELD_META[mode].name; equation.textContent = FIELD_META[mode].equation;
    modes.forEach(button => { const selected = button.dataset.field === mode; button.classList.toggle('active', selected); button.setAttribute('aria-pressed', String(selected)); });
    seedParticles();
  }
  function setPaused(nextPaused) {
    paused = nextPaused; pause.setAttribute('aria-pressed', String(paused));
    pause.innerHTML = paused ? '<span aria-hidden="true">▶</span> Retomar simulação' : '<span aria-hidden="true">Ⅱ</span> Pausar simulação';
    if (!paused) { last = performance.now(); animationId = requestAnimationFrame(draw); } else cancelAnimationFrame(animationId);
  }
  modes.forEach(button => button.addEventListener('click', () => setMode(button.dataset.field)));
  pause.addEventListener('click', () => setPaused(!paused));
  section.addEventListener('pointermove', event => { const rect = section.getBoundingClientRect(); pointer.x = event.clientX - rect.left; pointer.y = event.clientY - rect.top; pointer.active = true; });
  section.addEventListener('pointerleave', () => { pointer.active = false; });
  window.addEventListener('resize', resize, {passive: true}); resize();
  if (paused) { draw(0); paused = true; pause.innerHTML = '<span aria-hidden="true">▶</span> Ativar simulação'; pause.setAttribute('aria-pressed', 'true'); } else animationId = requestAnimationFrame(draw);
}

if (typeof document !== 'undefined') setupLab();
