I made this as a single HTML file using canvas and JS. Save it as `liquid-cat.html` and open it in a browser. I used canvas because SVG can't easily slice and warp a drawing column by column.

The cat is drawn as a sprite and cut into thin vertical slices. Each slice moves along the tube at a speed that depends on where it is. In the narrow part the slices move faster, so the cat stretches out and gets thinner (volume is roughly preserved), then re-forms as it leaves the exit funnel. The glass funnel shape is computed from the same flow function, so the walls match the liquid.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Liquid Cat</title>
<style>
  html,body{margin:0;height:100%;background:#12132a;}
  body{display:flex;align-items:center;justify-content:center;}
  canvas{width:min(100vw,1100px);height:auto;aspect-ratio:1100/250;display:block;cursor:pointer}
</style>
</head>
<body>
<canvas id="stage" title="click to restart"></canvas>
<script>
(() => {
'use strict';

/* ------------------------------------------------------------------ config */
const W = 1100, H = 250, CY = 125;           // scene size, tube centre line
const CW = 156, CH = 120, SC = 2;            // cat sprite size (+ supersampling)
const START_X = 34;                          // left edge of resting cat
const K = 3.2;                               // how much the cat is squeezed in the tube
const X_IN0 = 230, X_IN1 = 340;              // entry funnel
const X_OUT0 = 760, X_OUT1 = 870;            // exit funnel
const FLOOR = CY + 57;
const DPR = Math.min(window.devicePixelRatio || 1, 2);
const NCOL = CW * SC;

// timeline of one crossing (seconds)
const A0 = 0.9, A1 = A0 + 0.55, A2 = A1 + 0.18, A3 = A2 + 3.6, A4 = A3 + 1.5, A5 = A4 + 0.55;
const CYCLE = A5;

/* ------------------------------------------------------------------ canvases */
const cv  = document.getElementById('stage');
cv.width = W * DPR; cv.height = H * DPR;
const ctx = cv.getContext('2d');
const fc  = document.createElement('canvas'); fc.width = W * DPR; fc.height = H * DPR;
const f   = fc.getContext('2d');             // cat / liquid layer
const sp  = document.createElement('canvas'); sp.width = CW * SC; sp.height = CH * SC;
const c   = sp.getContext('2d');             // cat sprite

/* ------------------------------------------------------------------ helpers */
const clamp  = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
const ease   = p => p * p * (3 - 2 * p);
function rr(g, x, y, w, h, r) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

/* ------------------------------------------------------------------ flow field
   G(x): 0 outside the tube, 1 in the narrow part (smooth funnels).
   V(x): flow speed relative to the resting cat. Column height scales as 1/V,
         column width as V  -> the "liquid" keeps its volume.                   */
const G  = x => smooth(X_IN0, X_IN1, x) * (1 - smooth(X_OUT0, X_OUT1, x));
const V  = x => 1 + (K - 1) * G(x);
const RW = x => CH / (2 * V(x)) + 4;         // inner half-height of glass

// travel-time table T(x) = ∫ dx / V  (and its inverse)
const TX0 = -100, TSTEP = 0.5, TN = Math.round((1300 - TX0) / TSTEP) + 1;
const TT = new Float32Array(TN);
for (let i = 1; i < TN; i++) TT[i] = TT[i - 1] + TSTEP / V(TX0 + (i - 0.5) * TSTEP);
const T = x => {
  const u = (x - TX0) / TSTEP, i = clamp(Math.floor(u), 0, TN - 2);
  return TT[i] + (TT[i + 1] - TT[i]) * (u - i);
};
const Tinv = t => {
  let lo = 0, hi = TN - 1;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (TT[m] <= t) lo = m; else hi = m; }
  const d = TT[hi] - TT[lo];
  return TX0 + (lo + (d > 0 ? (t - TT[lo]) / d : 0)) * TSTEP;
};

const T0 = new Float32Array(NCOL + 1);
for (let i = 0; i <= NCOL; i++) T0[i] = T(START_X + i / SC);
const S_TOTAL = T(W - START_X) - T(START_X + CW);   // how far the "flow clock" runs

const P = new Float32Array(NCOL + 1);                // slice edge positions
function computeEdges(s) { for (let i = 0; i <= NCOL; i++) P[i] = Tinv(T0[i] + s); }

/* ------------------------------------------------------------------ the cat */
let clock = 0;
function drawSprite(q) {
  c.setTransform(SC, 0, 0, SC, 0, 0);
  c.clearRect(0, 0, CW, CH);
  c.lineJoin = 'round'; c.lineCap = 'round';
  const OR = '#f7a53f', OR2 = '#e58a25', DK = '#6b3410', CR = '#fff0d6', PK = '#ff8fa6', ST = '#c96a14';

  // tail
  const w = Math.sin(clock * 3.4) * q.tail;
  c.beginPath(); c.moveTo(28, 86);
  c.bezierCurveTo(6, 92, 4 + w * 0.6, 60, 12 + w, 32 + Math.abs(w) * 0.25);
  c.strokeStyle = DK; c.lineWidth = 13; c.stroke();
  c.strokeStyle = OR; c.lineWidth = 7.5; c.stroke();

  // far legs
  c.fillStyle = OR2; c.strokeStyle = DK; c.lineWidth = 2.6;
  for (const x of [47, 99]) {
    rr(c, x, 92, 13, 24, 6); c.fill(); c.stroke();
    c.beginPath(); c.ellipse(x + 6.5, 113, 5.2, 3.2, 0, 0, 7); c.fillStyle = CR; c.fill();
    c.fillStyle = OR2;
  }

  // body
  c.beginPath(); c.ellipse(66, 84, 46, 27, 0, 0, 7);
  c.fillStyle = OR; c.fill(); c.strokeStyle = DK; c.lineWidth = 3; c.stroke();
  c.beginPath(); c.ellipse(70, 98, 30, 10, 0, 0, 7); c.fillStyle = CR; c.fill();
  c.strokeStyle = ST; c.lineWidth = 4;
  for (const [x1, y1, x2, y2] of [[38, 64, 42, 74], [52, 59, 54, 70], [66, 58, 67, 69], [80, 59, 79, 70]]) {
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
  }

  // near legs
  c.strokeStyle = DK; c.lineWidth = 2.6;
  for (const x of [31, 83]) {
    rr(c, x, 92, 14, 24, 6.5); c.fillStyle = OR; c.fill(); c.stroke();
    c.beginPath(); c.ellipse(x + 7, 113, 5.6, 3.3, 0, 0, 7); c.fillStyle = CR; c.fill();
  }

  // ears (behind head)
  c.lineWidth = 3; c.strokeStyle = DK;
  c.beginPath(); c.moveTo(85, 44); c.lineTo(88, 9); c.lineTo(110, 32); c.closePath();
  c.fillStyle = OR; c.fill(); c.stroke();
  c.beginPath(); c.moveTo(90, 36); c.lineTo(91, 19); c.lineTo(103, 31); c.closePath();
  c.fillStyle = PK; c.fill();
  c.save(); c.translate(132, 36); c.rotate(q.twitch); c.translate(-132, -36);
  c.beginPath(); c.moveTo(115, 32); c.lineTo(137, 9); c.lineTo(141, 45); c.closePath();
  c.fillStyle = OR; c.fill(); c.strokeStyle = DK; c.lineWidth = 3; c.stroke();
  c.beginPath(); c.moveTo(121, 31); c.lineTo(134, 19); c.lineTo(136, 37); c.closePath();
  c.fillStyle = PK; c.fill();
  c.restore();

  // head
  c.beginPath(); c.ellipse(112, 57, 33, 28, 0, 0, 7);
  c.fillStyle = OR; c.fill(); c.strokeStyle = DK; c.lineWidth = 3; c.stroke();
  c.strokeStyle = ST; c.lineWidth = 3;
  for (const [x1, y1, x2, y2] of [[103, 31, 104, 38], [112, 30, 112, 39], [121, 31, 120, 38]]) {
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
  }

  // cheeks
  c.fillStyle = 'rgba(255,120,150,0.45)';
  for (const x of [88, 136]) { c.beginPath(); c.arc(x, 69, 5, 0, 7); c.fill(); }

  // eyes
  if (q.happy) {
    c.strokeStyle = DK; c.lineWidth = 3.2;
    for (const ex of [100, 124]) { c.beginPath(); c.arc(ex, 59, 6.5, Math.PI * 1.12, Math.PI * 1.88); c.stroke(); }
  } else {
    for (const ex of [100, 124]) {
      const rx = 8.5 * q.es, ry = Math.max(1, 10.5 * q.es * (1 - q.blink));
      c.beginPath(); c.ellipse(ex, 55, rx, ry, 0, 0, 7);
      c.fillStyle = '#fff'; c.fill(); c.strokeStyle = DK; c.lineWidth = 2.2; c.stroke();
      if (ry > 3) {
        c.beginPath(); c.ellipse(ex + q.lx, 55 + q.ly, 5 * q.es, Math.max(0.5, Math.min(6.5 * q.es, ry - 1.2)), 0, 0, 7);
        c.fillStyle = '#231208'; c.fill();
        c.beginPath(); c.arc(ex + q.lx + 1.8, 55 + q.ly - 2.2, 1.7, 0, 7); c.fillStyle = '#fff'; c.fill();
      }
    }
  }

  // mouth
  c.strokeStyle = DK; c.lineWidth = 1.8;
  if (q.open) {
    c.beginPath(); c.ellipse(112, 73, 5.5, 5, 0, 0, 7); c.fillStyle = '#5a1a1a'; c.fill(); c.stroke();
    c.beginPath(); c.ellipse(112, 75.5, 3.2, 2.2, 0, 0, 7); c.fillStyle = PK; c.fill();
  } else {
    c.beginPath(); c.moveTo(112, 67); c.lineTo(112, 70);
    c.arc(107.5, 70, 4.5, 0, Math.PI * 0.8);
    c.moveTo(112, 70); c.arc(116.5, 70, 4.5, Math.PI, Math.PI * 0.2, true);
    c.stroke();
  }
  // nose
  c.beginPath(); c.moveTo(108, 62); c.lineTo(116, 62); c.lineTo(112, 67); c.closePath();
  c.fillStyle = PK; c.fill(); c.lineWidth = 1.6; c.stroke();

  // whiskers
  c.strokeStyle = 'rgba(107,52,16,0.85)'; c.lineWidth = 1.3;
  for (const [x1, y1, x2, y2] of [[92, 67, 70, 62], [92, 70, 68, 70], [93, 73, 72, 79],
                                  [132, 67, 154, 62], [132, 70, 155, 70], [131, 73, 152, 79]]) {
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
  }
}

/* ------------------------------------------------------------------ glass tube (pre-built paths) */
const XS = []; for (let x = X_IN0 - 14; x <= X_OUT1 + 14; x += 2) XS.push(x);
function band(sign, a, b) {
  const p = new Path2D();
  XS.forEach((x, i) => { const y = CY + sign * (RW(x) + a); i ? p.lineTo(x, y) : p.moveTo(x, y); });
  for (let i = XS.length - 1; i >= 0; i--) p.lineTo(XS[i], CY + sign * (RW(XS[i]) + b));
  p.closePath(); return p;
}
function line(sign, a) {
  const p = new Path2D();
  XS.forEach((x, i) => { const y = CY + sign * (RW(x) + a); i ? p.lineTo(x, y) : p.moveTo(x, y); });
  return p;
}
const wallTop = band(-1, 0, 7), wallBot = band(1, 0, 7);
const glintTop = line(-1, 2.6), glintBot = line(1, 4.4);
const inside = (() => {
  const p = new Path2D();
  XS.forEach((x, i) => { const y = CY - RW(x); i ? p.lineTo(x, y) : p.moveTo(x, y); });
  for (let i = XS.length - 1; i >= 0; i--) p.lineTo(XS[i], CY + RW(XS[i]));
  p.closePath(); return p;
})();

const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
bgGrad.addColorStop(0, '#2a2d55'); bgGrad.addColorStop(1, '#151731');
const spot = ctx.createRadialGradient(550, 100, 20, 550, 100, 560);
spot.addColorStop(0, 'rgba(130,160,255,0.20)'); spot.addColorStop(1, 'rgba(130,160,255,0)');
const floorGrad = ctx.createLinearGradient(0, FLOOR, 0, H);
floorGrad.addColorStop(0, '#26295225'.slice(0, 7)); floorGrad.addColorStop(1, '#12132a');
const glintGrad = ctx.createLinearGradient(X_IN0, 0, X_OUT1, 0);
[[0, 0], [0.12, 0.75], [0.5, 0.35], [0.88, 0.75], [1, 0]].forEach(([o, a]) =>
  glintGrad.addColorStop(o, `rgba(255,255,255,${a})`));
const gloss = f.createLinearGradient(0, 0, 0, 1);
gloss.addColorStop(0, 'rgba(255,255,255,0.60)');
gloss.addColorStop(0.25, 'rgba(255,255,255,0.14)');
gloss.addColorStop(0.55, 'rgba(255,255,255,0)');
gloss.addColorStop(1, 'rgba(70,20,0,0.35)');

/* ------------------------------------------------------------------ particles & bubbles */
const parts = [];
const bubbles = Array.from({ length: 14 }, () => ({
  xs: 34 + Math.random() * 74, fy: 0.55 + Math.random() * 0.3, r: 0.9 + Math.random() * 1.5
}));
const colX = new Float32Array(NCOL), colY = new Float32Array(NCOL),
      colH = new Float32Array(NCOL), colG = new Float32Array(NCOL);

/* ------------------------------------------------------------------ pose over time */
function pose(lt) {
  const q = { s: 0, sx: 1, sy: 1, hop: 0, end: false, es: 1, happy: false, open: false,
              tail: 5, lx: 2.4, ly: 0, twitch: 0, blink: 0 };
  if (lt < A0) {                                   // idle
    const b = Math.sin(clock * 2.6); q.sy = 1 + 0.012 * b; q.sx = 1 - 0.006 * b;
  } else if (lt < A1) {                            // crouch
    const e = ease((lt - A0) / (A1 - A0));
    q.sy = 1 - 0.17 * e; q.sx = 1 + 0.09 * e; q.es = 1 + 0.15 * e; q.tail = 5 + 6 * e;
  } else if (lt < A2) {                            // spring
    const e = (lt - A1) / (A2 - A1), o = 1 - (1 - e) * (1 - e);
    q.sy = 0.83 + 0.27 * o; q.sx = 1.09 - 0.15 * o; q.es = 1.2; q.open = true; q.tail = 10;
  } else if (lt < A3) {                            // FLOW
    const p = (lt - A2) / (A3 - A2);
    q.s = S_TOTAL * ease(p);
    const k = Math.max(0, 1 - (lt - A2) / 0.28);
    q.sy = 1 + 0.10 * k; q.sx = 1 - 0.06 * k; q.es = 1.2; q.open = p < 0.93; q.tail = 10;
  } else if (lt < A4) {                            // land + jiggle
    const tau = lt - A3, w = Math.exp(-4.2 * tau) * Math.sin(17 * tau);
    q.s = S_TOTAL; q.end = true; q.sy = 1 - 0.2 * w; q.sx = 1 + 0.16 * w;
    q.happy = tau < 1.25; q.open = tau < 1.0; q.tail = 9; q.lx = 0;
  } else {                                         // turn around
    const p = (lt - A4) / (A5 - A4);
    q.s = S_TOTAL; q.end = true; q.sx = Math.cos(Math.PI * p);
    q.hop = Math.sin(Math.PI * p) * 16; q.lx = 0;
  }
  if (Math.abs(q.sx) < 0.02) q.sx = q.sx < 0 ? -0.02 : 0.02;
  const ph = clock % 3.1;
  q.blink = ph < 0.16 ? Math.sin(Math.PI * ph / 0.16) : 0;
  q.twitch = Math.sin(clock * 0.8) > 0.96 ? Math.sin(clock * 40) * 0.18 : 0;
  return q;
}

/* ------------------------------------------------------------------ drawing */
function drawCat(q) {
  drawSprite(q);
  f.setTransform(DPR, 0, 0, DPR, 0, 0);
  f.clearRect(0, 0, W, H);
  f.imageSmoothingEnabled = true; f.imageSmoothingQuality = 'high';

  f.save();
  const bx = q.end ? W - START_X - CW / 2 : START_X + CW / 2, by = FLOOR;
  f.translate(bx, by - q.hop); f.scale(q.sx, q.sy); f.translate(-bx, -by);

  const tailX = P[0], noseX = P[NCOL];
  if (noseX <= X_IN0 || tailX >= X_OUT1) {
    // fully outside the tube: draw crisp, in one piece
    f.drawImage(sp, tailX, CY - CH / 2, CW, CH);
  } else {
    for (let i = 0; i < NCOL; i++) {
      const xl = P[i], xr = P[i + 1], xm = (xl + xr) / 2, gg = G(xm);
      let h = CH / (1 + (K - 1) * gg), yc = CY;
      if (gg > 0) {                                 // sloshing
        yc += Math.sin(xm * 0.045 - clock * 9) * 2.2 * gg;
        h  *= 1 + 0.07 * gg * Math.sin(xm * 0.08 + clock * 7);
      }
      const top = yc - h / 2, dw = xr - xl + 0.8;
      f.drawImage(sp, i, 0, 1, CH * SC, xl, top, dw, h);
      if (gg > 0.03) {                              // wet gloss, only on cat pixels
        f.save();
        f.globalCompositeOperation = 'source-atop'; f.globalAlpha = gg;
        f.translate(xl, top); f.scale(1, h);
        f.fillStyle = gloss; f.fillRect(0, 0, dw, 1);
        f.restore();
      }
      colX[i] = xm; colY[i] = yc; colH[i] = h; colG[i] = gg;
    }
    // bubbles riding along inside the liquid
    for (const b of bubbles) {
      const i = Math.min(NCOL - 1, Math.round(b.xs * SC)), gg = colG[i];
      if (gg < 0.6) continue;
      const fy = b.fy + 0.035 * Math.sin(clock * 3 + b.xs);
      const x = colX[i], y = colY[i] - colH[i] / 2 + fy * colH[i];
      f.globalAlpha = (gg - 0.6) / 0.4;
      f.beginPath(); f.arc(x, y, b.r, 0, 7);
      f.fillStyle = 'rgba(255,255,255,0.28)'; f.fill();
      f.strokeStyle = 'rgba(255,255,255,0.8)'; f.lineWidth = 0.8; f.stroke();
    }
    f.globalAlpha = 1;
  }
  f.restore();

  // particles (droplets + sparkles)
  for (const p of parts) {
    const a = 1 - p.age / p.life;
    if (p.k === 'd') {
      f.globalAlpha = Math.min(1, a * 1.6);
      f.beginPath(); f.arc(p.x, p.y, p.r, 0, 7);
      f.fillStyle = '#f7a53f'; f.fill(); f.strokeStyle = '#c96a14'; f.lineWidth = 0.8; f.stroke();
    } else {
      f.save(); f.translate(p.x, p.y); f.rotate(p.age * 2); f.globalAlpha = a;
      const r = p.r * (0.7 + 0.3 * Math.sin(p.age * 14));
      f.beginPath();
      for (let k = 0; k < 8; k++) {
        const rad = k % 2 ? r * 0.35 : r, ang = k * Math.PI / 4;
        f.lineTo(Math.cos(ang) * rad, Math.sin(ang) * rad);
      }
      f.closePath(); f.fillStyle = '#ffe680'; f.fill(); f.restore();
    }
  }
  f.globalAlpha = 1;
}

function drawShadow() {
  const a = P[0] + 6, b = P[NCOL] - 6;
  if (b - a < 20) return;
  ctx.save();
  ctx.beginPath(); ctx.rect(0, 0, X_IN0, H); ctx.rect(X_OUT1, 0, W - X_OUT1, H); ctx.clip();
  ctx.fillStyle = 'rgba(0,0,0,0.14)';
  for (let k = 0; k < 3; k++) {
    const e = k * 3;
    rr(ctx, a - e, FLOOR + 1 - e * 0.3, (b - a) + 2 * e, 6 + e * 0.6, 3 + e * 0.3); ctx.fill();
  }
  ctx.restore();
}

function drawTubeFront() {
  ctx.save();
  ctx.fillStyle = 'rgba(185,220,255,0.20)';
  ctx.strokeStyle = 'rgba(230,245,255,0.6)'; ctx.lineWidth = 1.4;
  for (const p of [wallTop, wallBot]) { ctx.fill(p); ctx.stroke(p); }
  ctx.lineWidth = 1.8; ctx.strokeStyle = glintGrad; ctx.stroke(glintTop);
  ctx.lineWidth = 1.2; ctx.globalAlpha = 0.4; ctx.stroke(glintBot); ctx.globalAlpha = 1;
  ctx.fillStyle = 'rgba(235,247,255,0.55)';
  for (const x of [X_IN0 - 14, X_OUT1 + 14]) for (const s of [-1, 1]) {
    rr(ctx, x - 4, CY + s * (RW(x) + 3.5) - 6, 8, 12, 4); ctx.fill();
  }
  ctx.restore();
}

let dir = 1;
function render() {
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = bgGrad; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = spot;   ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#1b1d3d'; ctx.fillRect(0, FLOOR, W, H - FLOOR);
  ctx.fillStyle = 'rgba(255,255,255,0.07)'; ctx.fillRect(0, FLOOR, W, 1.5);

  ctx.save();
  if (dir < 0) { ctx.translate(W, 0); ctx.scale(-1, 1); }
  drawShadow();
  ctx.restore();

  ctx.fillStyle = 'rgba(120,170,255,0.09)'; ctx.fill(inside);

  ctx.save();
  if (dir < 0) { ctx.translate(W, 0); ctx.scale(-1, 1); }
  ctx.drawImage(fc, 0, 0, W, H);
  ctx.restore();

  drawTubeFront();
}

/* ------------------------------------------------------------------ simulation step */
let lastCycle = 0, prevS = 0, starsDone = false, acc1 = 0, acc2 = 0;
const rnd = (a, b) => a + Math.random() * (b - a);

function step(dt) {
  clock += dt;
  const cyc = Math.floor(clock / CYCLE);
  if (cyc !== lastCycle) { lastCycle = cyc; starsDone = false; prevS = 0; }
  dir = cyc % 2 === 0 ? 1 : -1;
  const lt = clock - cyc * CYCLE;

  const q = pose(lt);
  computeEdges(q.s);
  const ds = dt > 0 ? (q.s - prevS) / dt : 0; prevS = q.s;

  // splashes at the two mouths
  if (lt >= A2 && lt < A3 && ds > 5) {
    const sp_ = clamp(ds / 220, 0, 2), tailX = P[0], noseX = P[NCOL];
    if (noseX > X_IN0 && tailX < X_IN0 + 30) {
      acc1 += dt * 38 * sp_;
      while (acc1 >= 1) { acc1--; parts.push({ k: 'd', x: X_IN0 + rnd(0, 20), y: CY + rnd(-25, 25),
        vx: -rnd(30, 140), vy: -rnd(50, 220), r: rnd(1.4, 3.6), life: rnd(0.5, 0.9), age: 0 }); }
    }
    if (noseX > X_OUT0 && tailX < X_OUT1) {
      acc2 += dt * 38 * sp_;
      while (acc2 >= 1) { acc2--; parts.push({ k: 'd', x: X_OUT1 - rnd(0, 20), y: CY + rnd(-25, 25),
        vx: rnd(30, 160), vy: -rnd(50, 220), r: rnd(1.4, 3.6), life: rnd(0.5, 0.9), age: 0 }); }
    }
  }
  // sparkles on landing
  if (lt >= A3 && !starsDone) {
    starsDone = true;
    const cx = W - START_X - CW / 2;
    for (let i = 0; i < 9; i++) {
      const a = rnd(0, 6.28), r = rnd(30, 85);
      parts.push({ k: 's', x: cx + Math.cos(a) * r, y: CY - 10 + Math.sin(a) * r * 0.5,
        vx: rnd(-15, 15), vy: -rnd(15, 50), r: rnd(4, 8), life: rnd(0.8, 1.3), age: 0 });
    }
  }
  for (let i = parts.length - 1; i >= 0; i--) {
    const p = parts[i];
    p.age += dt; p.x += p.vx * dt; p.y += p.vy * dt;
    if (p.k === 'd') p.vy += 700 * dt;
    if (p.age > p.life || p.y > FLOOR + 2) parts.splice(i, 1);
  }
  return q;
}

/* ------------------------------------------------------------------ main loop */
let last = performance.now();
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  const q = step(dt);
  drawCat(q);
  render();
  requestAnimationFrame(frame);
}
cv.addEventListener('click', () => { clock = 0; lastCycle = 0; prevS = 0; parts.length = 0; });
requestAnimationFrame(frame);
})();
</script>
</body>
</html>
```

**What happens:** the cat sits and blinks, crouches, then gets sucked into the glass funnel and squeezed through the tube as an orange stripe with bubbles and a wet gloss. It re-forms at the other end with a splash, a jiggle and sparkles, then turns around and does the trip in reverse. Clicking the canvas restarts it.

**Things to tweak:**
- `K` sets how squeezed the cat gets (bigger means thinner and longer in the tube).
- `X_IN0`, `X_IN1`, `X_OUT0` and `X_OUT1` set the funnel and tube geometry.
- `A0`–`A5` set the timing. The flow lasts `A3 - A2`, which is 3.6 seconds.

I haven't run it in a browser, so if anything looks off, tell me what you see and I'll adjust it.