Here's a self-contained HTML file with an SVG scene animated by JavaScript. A cartoon cat walks up to a glass lab tube, melts into it, flows through the bends, and pours out the other end, where it re-forms. Then it walks off and the loop starts again.

The liquid look comes from an SVG "gooey" filter. The cat is built from simple shapes (circles, ellipses and thick strokes) that get blurred and then alpha-thresholded, so any shapes that touch fuse into one blob. A dilate step adds the cartoon outline. The part of the cat inside the tube is a stroke of the tube's own path, trimmed with `stroke-dasharray`, so it follows the tube exactly.

Save this as `liquid-cat.html` and open it in a browser:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Cats Are Liquid</title>
<style>
  html, body { margin: 0; background: #221c2b; }
  body {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 14px; padding: 16px; box-sizing: border-box; min-height: 100vh;
    font-family: "Comic Sans MS", "Chalkboard SE", "Comic Neue", system-ui, sans-serif;
    color: #f3e7d9;
  }
  svg { width: min(100%, 1200px); height: auto; display: block; border-radius: 20px;
        box-shadow: 0 12px 50px rgba(0,0,0,.45); }
  .controls { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
  button { font: inherit; font-size: 15px; background: #3a3046; color: #f3e7d9;
           border: 2px solid #5b4b6e; border-radius: 999px; padding: 6px 16px; cursor: pointer; }
  button:hover { background: #4a3d59; }
  button.on { background: #f59e42; border-color: #f59e42; color: #2a1a10; }
  .fx { font-weight: 700; paint-order: stroke; stroke: #3b2314; stroke-width: 6px;
        stroke-linejoin: round; fill: #fff; }
</style>
</head>
<body>

<svg id="scene" viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff6e8"/><stop offset="1" stop-color="#ffe2c0"/>
    </linearGradient>
    <pattern id="dots" width="44" height="44" patternUnits="userSpaceOnUse">
      <circle cx="11" cy="11" r="2.5" fill="#f6d6b0"/><circle cx="33" cy="33" r="2.5" fill="#f6d6b0"/>
    </pattern>
    <linearGradient id="floorG" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#d8a673"/><stop offset="1" stop-color="#bf8a58"/>
    </linearGradient>
    <linearGradient id="metal" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7d8b99"/><stop offset=".5" stop-color="#c9d3dc"/><stop offset="1" stop-color="#7d8b99"/>
    </linearGradient>

    <!-- The magic: blur + alpha threshold = metaball "goo", then dilate for a cartoon outline -->
    <filter id="goo" filterUnits="userSpaceOnUse" x="0" y="0" width="1200" height="600"
            color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur"/>
      <feColorMatrix in="blur" mode="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 16 -6.5" result="goo"/>
      <feMorphology in="goo" operator="dilate" radius="3" result="fat"/>
      <feFlood flood-color="#3b2314" result="ink"/>
      <feComposite in="ink" in2="fat" operator="in" result="outline"/>
      <feMerge><feMergeNode in="outline"/><feMergeNode in="goo"/></feMerge>
    </filter>
  </defs>

  <!-- Room -->
  <rect width="1200" height="600" fill="url(#wall)"/>
  <rect width="1200" height="470" fill="url(#dots)"/>
  <rect y="480" width="1200" height="120" fill="url(#floorG)"/>
  <g stroke="#b17d4c" stroke-width="2" opacity=".55">
    <line x1="0" y1="522" x2="1200" y2="522"/><line x1="0" y1="566" x2="1200" y2="566"/>
    <line x1="160" y1="480" x2="160" y2="522"/><line x1="520" y1="480" x2="520" y2="522"/>
    <line x1="880" y1="480" x2="880" y2="522"/><line x1="330" y1="522" x2="330" y2="566"/>
    <line x1="720" y1="522" x2="720" y2="566"/><line x1="1080" y1="522" x2="1080" y2="566"/>
  </g>
  <rect y="466" width="1200" height="16" fill="#fff3e2" stroke="#d9b48c" stroke-width="2"/>

  <!-- Fish painting -->
  <g transform="translate(60 96) rotate(-3)">
    <rect width="132" height="98" rx="6" fill="#fffaf2" stroke="#8a5a33" stroke-width="8"/>
    <path d="M86 50 L108 35 L108 65 Z" fill="#6fb7e8" stroke="#3b2314" stroke-width="2.5" stroke-linejoin="round"/>
    <ellipse cx="60" cy="50" rx="30" ry="17" fill="#6fb7e8" stroke="#3b2314" stroke-width="2.5"/>
    <circle cx="44" cy="45" r="3" fill="#3b2314"/>
    <path d="M54 39 Q60 50 54 61" fill="none" stroke="#3b2314" stroke-width="2"/>
  </g>

  <!-- Clock -->
  <g transform="translate(1100 118)">
    <circle r="42" fill="#fffaf2" stroke="#8a5a33" stroke-width="7"/>
    <g stroke="#8a5a33" stroke-width="3" stroke-linecap="round">
      <line y1="-32" y2="-26"/><line y1="32" y2="26"/><line x1="-32" x2="-26"/><line x1="32" x2="26"/>
    </g>
    <line id="hourHand" x1="0" y1="0" x2="0" y2="-18" stroke="#3b2314" stroke-width="5" stroke-linecap="round"/>
    <line id="minHand" x1="0" y1="0" x2="0" y2="-28" stroke="#3b2314" stroke-width="3" stroke-linecap="round"/>
    <circle r="4" fill="#3b2314"/>
  </g>

  <text x="600" y="66" text-anchor="middle" font-size="42" font-weight="700" fill="#7a4521">Cats are liquid.</text>
  <text x="600" y="94" text-anchor="middle" font-size="17" fill="#a3734d">a completely scientific demonstration</text>

  <!-- Shadow -->
  <ellipse id="shadow" fill="#5a3517"/>

  <!-- Tube supports -->
  <g>
    <rect x="381" y="436" width="8" height="46" fill="url(#metal)"/>
    <rect x="673" y="286" width="8" height="196" fill="url(#metal)"/>
    <rect x="901" y="420" width="8" height="62" fill="url(#metal)"/>
    <rect x="667" y="279" width="20" height="12" rx="3" fill="#8795a3" stroke="#5e6b78" stroke-width="2"/>
    <g fill="#8795a3" stroke="#5e6b78" stroke-width="2">
      <ellipse cx="385" cy="481" rx="20" ry="5"/><ellipse cx="677" cy="481" rx="24" ry="6"/><ellipse cx="905" cy="481" rx="20" ry="5"/>
    </g>
  </g>

  <!-- Tube: back layer -->
  <g>
    <path class="tubeD" fill="none" stroke="#56789a" stroke-width="42" stroke-linejoin="round"/>
    <path class="tubeD" id="tubeRef" fill="none" stroke="#e4f3fd" stroke-width="34" stroke-linejoin="round"/>
    <path d="M355 345 L412 381 L412 419 L355 455 Z" fill="#e4f3fd"/>
    <path d="M355 345 L412 381 M355 455 L412 419" fill="none" stroke="#56789a" stroke-width="4" stroke-linecap="round"/>
    <ellipse cx="355" cy="400" rx="12" ry="55" fill="#c7e1f3" stroke="#56789a" stroke-width="4"/>
    <path d="M916 381 L938 372 L938 428 L916 419 Z" fill="#e4f3fd"/>
    <path d="M916 381 L938 372 M916 419 L938 428" fill="none" stroke="#56789a" stroke-width="4" stroke-linecap="round"/>
    <ellipse cx="938" cy="400" rx="7" ry="28" fill="#c7e1f3" stroke="#56789a" stroke-width="4"/>
  </g>

  <!-- The cat (everything in here gets gooified) -->
  <g id="cat" filter="url(#goo)">
    <path id="tail" fill="none" stroke="#f59e42" stroke-linecap="round"/>
    <ellipse id="body" fill="#f59e42"/>
    <ellipse id="paw0" fill="#f59e42"/><ellipse id="paw1" fill="#f59e42"/><ellipse id="paw2" fill="#f59e42"/>
    <line id="conn" stroke="#f59e42" stroke-linecap="round"/>
    <line id="neck" stroke="#f59e42" stroke-linecap="round"/>
    <path id="stream" class="tubeD" fill="none" stroke="#f59e42" stroke-width="22" stroke-linecap="round" style="display:none"/>
    <circle class="blob" fill="#f59e42"/><circle class="blob" fill="#f59e42"/><circle class="blob" fill="#f59e42"/>
    <circle class="blob" fill="#f59e42"/><circle class="blob" fill="#f59e42"/>
    <path id="earL" fill="#f59e42"/><path id="earR" fill="#f59e42"/>
    <circle id="head" fill="#f59e42"/>
  </g>

  <!-- Non-goo details on top of the cat -->
  <g id="bodyStripes" fill="none" stroke="#dc7a22" stroke-width="5" stroke-linecap="round">
    <path d="M -42 -40 Q -34 -30 -42 -18"/><path d="M -20 -50 Q -13 -38 -21 -26"/><path d="M 2 -52 Q 9 -40 1 -28"/>
  </g>
  <g id="innerEars" fill="#ffb3c1"><path id="innerL"/><path id="innerR"/></g>
  <g id="face">
    <g id="details">
      <g stroke="#dc7a22" stroke-width="4.5" stroke-linecap="round" fill="none">
        <path d="M -9 -40 L -7 -29"/><path d="M 0 -42 L 0 -30"/><path d="M 9 -40 L 7 -29"/>
      </g>
      <ellipse cx="-27" cy="13" rx="7" ry="4" fill="#ff7f7f" opacity=".45"/>
      <ellipse cx="27" cy="13" rx="7" ry="4" fill="#ff7f7f" opacity=".45"/>
      <path d="M -5 6 L 5 6 L 0 11.5 Z" fill="#ff7d93" stroke="#3b2314" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M -9 14 Q -4.5 20 0 13 Q 4.5 20 9 14" fill="none" stroke="#3b2314" stroke-width="2.5" stroke-linecap="round"/>
      <g stroke="#3b2314" stroke-width="1.8" stroke-linecap="round">
        <line x1="24" y1="8" x2="54" y2="2"/><line x1="24" y1="14" x2="54" y2="17"/>
        <line x1="-24" y1="8" x2="-54" y2="2"/><line x1="-24" y1="14" x2="-54" y2="17"/>
      </g>
    </g>
    <g id="eyeL"><ellipse rx="7" ry="9" fill="#2a1a10"/><circle cx="2.2" cy="-3.2" r="2.6" fill="#fff"/></g>
    <g id="eyeR"><ellipse rx="7" ry="9" fill="#2a1a10"/><circle cx="2.2" cy="-3.2" r="2.6" fill="#fff"/></g>
    <path id="happyL" d="M -24 -2 Q -17 -12 -10 -2" fill="none" stroke="#2a1a10" stroke-width="3.5" stroke-linecap="round"/>
    <path id="happyR" d="M 10 -2 Q 17 -12 24 -2" fill="none" stroke="#2a1a10" stroke-width="3.5" stroke-linecap="round"/>
  </g>

  <!-- Tube: front glass layer -->
  <g pointer-events="none">
    <path class="tubeD" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="34"/>
    <path class="tubeD" fill="none" stroke="#fff" stroke-opacity=".75" stroke-width="4" stroke-linecap="round"
          stroke-dasharray="70 45 12 110" transform="translate(-6 -7)"/>
    <path d="M355 345 L412 381 L412 419 L355 455 Z" fill="#fff" fill-opacity=".14"/>
    <path d="M364 360 L404 385" stroke="#fff" stroke-opacity=".8" stroke-width="4" stroke-linecap="round"/>
    <ellipse cx="355" cy="400" rx="12" ry="55" fill="none" stroke="#56789a" stroke-width="4" opacity=".85"/>
    <ellipse cx="938" cy="400" rx="7" ry="28" fill="none" stroke="#56789a" stroke-width="4" opacity=".85"/>
  </g>

  <g id="sparkles"></g>
  <text id="fx" class="fx" font-size="30" text-anchor="middle" opacity="0"></text>
  <g id="bubble" opacity="0">
    <rect id="bubbleRect" y="-26" height="44" rx="20" fill="#fff" stroke="#3b2314" stroke-width="3"/>
    <path id="bubbleTail" fill="#fff" stroke="#3b2314" stroke-width="3" stroke-linejoin="round"/>
    <text id="bubbleText" y="-4" text-anchor="middle" dominant-baseline="middle" font-size="22" fill="#3b2314"></text>
  </g>
</svg>

<div class="controls">
  <button id="play">⏸ Pause</button>
  <button data-speed="0.5">0.5×</button>
  <button data-speed="1" class="on">1×</button>
  <button data-speed="2">2×</button>
  <button id="restart">↺ Restart</button>
</div>

<script>
(() => {
  const $ = id => document.getElementById(id);
  const NS = 'http://www.w3.org/2000/svg';

  // ---------- Tube geometry ----------
  const D = "M 370 400 L 420 400 C 480 400 490 330 490 270 C 490 160 600 140 630 220 " +
            "C 655 285 700 285 725 220 C 760 130 850 150 850 250 C 850 350 860 400 900 400 L 920 400";
  document.querySelectorAll('.tubeD').forEach(p => p.setAttribute('d', D));
  const ref = $('tubeRef');
  const T = ref.getTotalLength();
  const pt = s => ref.getPointAtLength(Math.max(0, Math.min(T, s)));
  const P0 = pt(0), PE = pt(T);

  // ---------- Constants ----------
  const FLOOR = 480;
  const L_CAT = 330;        // how long the cat is when squeezed into the tube
  const TAIL_EXTRA = 80;    // extra travel for the tail to pop out
  const START_X = 200, APPROACH_X = 258, FX = PE.x + 145;
  const FLOW_TOTAL = T + L_CAT + TAIL_EXTRA;

  const PHASES = [
    { n: 'idle', d: 1.9 }, { n: 'walkTo', d: 0.9 }, { n: 'squeeze', d: 0.8 },
    { n: 'flow', d: FLOW_TOTAL / 290 }, { n: 'celebrate', d: 2.6 },
    { n: 'walkOff', d: 1.5 }, { n: 'walkIn', d: 2.0 },
  ];
  const TOTAL = PHASES.reduce((a, p) => a + p.d, 0);

  // ---------- Easing helpers ----------
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = t => t * t * (3 - 2 * t);
  const easeInOut = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const easeOutCubic = t => 1 - Math.pow(1 - t, 3);
  const easeOutBack = t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
  const blink = t => { const p = t % 3.7; return p < .16 ? Math.max(.08, Math.abs(p - .08) / .08) : 1; };

  // ---------- Cat geometry ----------
  function tailRest(cx, time, bob = 0, amp = 1) {
    const w = time * 2.6;
    return { x0: cx - 70, y0: FLOOR - 40 + bob, x1: cx - 140, y1: FLOOR - 22 + bob,
             x2: cx - 118 + Math.sin(w) * 12 * amp, y2: FLOOR - 135 + bob + Math.cos(w) * 5 * amp, w: 18 };
  }
  function pawsRest(cx, walk = 0, wAmp = 0, lift = 0) {
    const s = Math.sin(walk);
    return [
      { x: cx + 46 + s * wAmp, y: FLOOR - 8 - Math.max(0, s) * wAmp * .7 + lift, s: 1 },
      { x: cx + 14 - s * wAmp, y: FLOOR - 8 - Math.max(0, -s) * wAmp * .7 + lift, s: 1 },
      { x: cx - 50 - s * wAmp * .8, y: FLOOR - 8 - Math.max(0, -s) * wAmp * .5 + lift, s: 1 },
    ];
  }
  function restGeom(cx, time, o = {}) {
    const bob = o.bob || 0, sq = o.sq || 0;
    const ry = 55 * (1 - sq), rx = 78 * (1 + sq * .6);
    const body = { x: cx, y: FLOOR - ry - 2 + bob, rx, ry };
    const head = { x: cx + 62, y: FLOOR - 118 + bob * 1.15 + sq * 70, r: 46 };
    return {
      body, head,
      tail: tailRest(cx, time, bob, o.tailAmp || 1),
      paws: pawsRest(cx, o.walk || 0, o.wAmp || 0, o.lift || 0),
      neck: { x1: body.x, y1: body.y, x2: head.x, y2: head.y, w: 50 },
      ears: 1, eyeOpen: blink(time), happy: false,
    };
  }

  // q: 0..1 squeeze progress (head into funnel); s: arc-length of the head along the tube
  function flowGeom(q, s, time) {
    const st = { ears: 1, eyeOpen: 1, happy: false, paws: [] };
    const cx = APPROACH_X;
    const rest = restGeom(cx, time);

    // Head
    if (q < 1) {
      const e = easeInOut(q);
      st.head = { x: lerp(rest.head.x, P0.x, e), y: lerp(rest.head.y, P0.y, e), r: lerp(46, 14, e) };
      st.ears = lerp(1, .85, e);
      st.eyeOpen = lerp(1, .2, clamp(q * 2.5));
    } else if (s <= T) {
      const p = pt(s);
      st.head = { x: p.x, y: p.y, r: 14 + Math.sin(time * 14) * .7 };
      st.ears = .85;
      st.eyeOpen = Math.min(lerp(.2, 1, clamp(s / 90)), blink(time));
    } else {
      const X = s - T, p = clamp(X / 130), e = easeOutCubic(p);
      st.head = { x: lerp(PE.x, FX + 62, e), y: lerp(PE.y, FLOOR - 118, e), r: 14 + 32 * easeOutBack(p) };
      st.ears = lerp(.85, 1, easeOutBack(clamp((p - .3) / .7)));
      st.eyeOpen = 1;
    }

    // Source side: the cat draining into the funnel
    const src = q < 1 ? 1 : clamp(1 - s / L_CAT);
    if (src > 0) {
      const qq = q < 1 ? q : 1;
      const melt = q < 1 ? .3 * smooth(q) : .3 + .7 * (1 - src);
      const k = Math.sqrt(src), drain = 1 - src;
      const rx = 78 * k * (1 + .25 * melt), ry = 55 * k * (1 - .35 * melt);
      const bx = lerp(cx, P0.x, Math.pow(drain, 1.2));
      const by = lerp(FLOOR - ry - 2, P0.y, drain * drain);
      st.body = { x: bx, y: by, rx, ry };

      const pawS = 1 - smooth(qq);
      if (pawS > 0) st.paws = rest.paws.map(p => ({ x: lerp(p.x, bx, 1 - pawS), y: p.y, s: pawS }));

      const tailK = clamp(src / .35), tk = easeInOut(tailK);
      const tr = tailRest(cx, time, 0, 1 + 2 * smooth(qq)); // frantic wag while draining
      const x0 = bx - rx * .9, y0 = by + ry * .3;
      st.tail = {
        x0, y0,
        x1: lerp((x0 + P0.x) / 2, tr.x1, tk), y1: lerp((y0 + P0.y) / 2, tr.y1, tk),
        x2: lerp(P0.x, tr.x2, tk), y2: lerp(P0.y, tr.y2, tk),
        w: 18 * (.55 + .45 * tailK) * clamp(src / .05),
      };
      if (q < 1) st.neck = { x1: bx, y1: by, x2: st.head.x, y2: st.head.y, w: lerp(50, 40, easeInOut(q)) };
      else st.conn = { x1: bx, y1: by, x2: P0.x, y2: P0.y, w: 22 + 18 * src };
    }

    // In the tube
    if (s > 0) {
      const a = Math.max(0, s - L_CAT), b = Math.min(T, s);
      if (b - a > .5) st.stream = { a, b };
    }

    // Destination side: the cat re-forming
    if (s > T) {
      const X = s - T, dst = clamp(X / L_CAT), lag = 1 - dst, k = Math.sqrt(dst);
      const rx = 78 * k * (1 + .25 * lag), ry = 55 * k * (1 - .3 * lag);
      const bx = lerp(PE.x + 20, FX, easeOutCubic(dst));
      const by = lerp(PE.y + 5, FLOOR - ry - 2, smooth(clamp(dst * 1.6)));
      st.body = { x: bx, y: by, rx, ry };
      st.neck = { x1: bx, y1: by, x2: st.head.x, y2: st.head.y, w: lerp(22, 50, dst) };
      if (X < L_CAT) st.conn = { x1: PE.x, y1: PE.y, x2: bx, y2: by, w: lerp(18, 30, lag) };

      const pawS = easeOutBack(clamp((X - L_CAT * .8) / 70));
      if (pawS > 0) st.paws = pawsRest(FX).map(p => ({ ...p, s: pawS }));

      if (X >= L_CAT) {
        const to = easeOutBack(clamp((X - L_CAT) / TAIL_EXTRA));
        const tr = tailRest(FX, time);
        const x0 = bx - rx * .9, y0 = by + ry * .3;
        st.tail = {
          x0, y0,
          x1: lerp((x0 + PE.x) / 2, tr.x1, to), y1: lerp((y0 + PE.y) / 2 + 15, tr.y1, to),
          x2: lerp(PE.x, tr.x2, to), y2: lerp(PE.y, tr.y2, to), w: 18,
        };
      }
    }
    return st;
  }

  // ---------- Rendering ----------
  const E = {};
  ['tail','body','paw0','paw1','paw2','conn','neck','stream','head','earL','earR','innerL','innerR',
   'innerEars','face','details','eyeL','eyeR','happyL','happyR','shadow','bodyStripes']
    .forEach(id => E[id] = $(id));
  const blobs = [...document.querySelectorAll('.blob')];
  const attrs = (el, o) => { for (const k in o) el.setAttribute(k, o[k]); };
  const vis = (el, on) => { el.style.display = on ? '' : 'none'; };
  const setLine = (el, l) => { vis(el, !!l); if (l) attrs(el, { x1: l.x1, y1: l.y1, x2: l.x2, y2: l.y2, 'stroke-width': l.w }); };

  const EAR_OUT = [[12, -38], [36, -72], [45, -12]];
  const EAR_IN  = [[20, -36], [34, -60], [38, -22]];
  const earD = (h, sc, side, pts) =>
    'M' + pts.map(([x, y]) => `${(h.x + side * x * sc).toFixed(1)} ${(h.y + y * sc).toFixed(1)}`).join(' L') + 'Z';

  function render(st, time) {
    const b = st.body, hasBody = !!b && b.rx > .6;
    vis(E.body, hasBody); vis(E.shadow, hasBody); vis(E.bodyStripes, hasBody);
    if (hasBody) {
      attrs(E.body, { cx: b.x, cy: b.y, rx: b.rx, ry: b.ry });
      const lift = Math.max(0, (FLOOR - 2) - (b.y + b.ry)), f = Math.max(.3, 1 - lift / 120);
      attrs(E.shadow, { cx: b.x + 12, cy: FLOOR + 5, rx: b.rx * 1.35 * f, ry: 10 * f, opacity: .22 * f });
      E.bodyStripes.setAttribute('opacity', clamp((b.rx / 78 - .45) / .35));
      E.bodyStripes.setAttribute('transform', `translate(${b.x} ${b.y}) scale(${b.rx / 78} ${b.ry / 55})`);
    }

    const tl = st.tail, hasTail = !!tl && tl.w > .5;
    vis(E.tail, hasTail);
    if (hasTail) {
      E.tail.setAttribute('d', `M${tl.x0} ${tl.y0} Q${tl.x1} ${tl.y1} ${tl.x2} ${tl.y2}`);
      E.tail.setAttribute('stroke-width', tl.w);
    }

    for (let i = 0; i < 3; i++) {
      const p = st.paws && st.paws[i], el = E['paw' + i], on = !!p && p.s > .02;
      vis(el, on);
      if (on) attrs(el, { cx: p.x, cy: p.y, rx: 17 * p.s, ry: 10 * p.s });
    }

    setLine(E.conn, st.conn);
    setLine(E.neck, st.neck);

    const sm = st.stream;
    vis(E.stream, !!sm);
    if (sm) {
      E.stream.setAttribute('stroke-dasharray', `${sm.b - sm.a} ${T * 3}`);
      E.stream.setAttribute('stroke-dashoffset', -sm.a);
    }
    // peristaltic bulges travelling through the cat-stream
    blobs.forEach((c, i) => {
      const on = !!sm && sm.b - sm.a > 40;
      vis(c, on);
      if (!on) return;
      const u = (i / blobs.length + time * .55) % 1;
      const p = pt(lerp(sm.a + 8, sm.b - 14, u));
      attrs(c, { cx: p.x, cy: p.y, r: 12 + 1.6 * Math.sin(time * 7 + i * 2.1) });
    });

    const h = st.head, k = h.r / 46, es = k * st.ears;
    attrs(E.head, { cx: h.x, cy: h.y, r: h.r });
    E.earL.setAttribute('d', earD(h, es, -1, EAR_OUT));
    E.earR.setAttribute('d', earD(h, es, 1, EAR_OUT));
    E.innerL.setAttribute('d', earD(h, es, -1, EAR_IN));
    E.innerR.setAttribute('d', earD(h, es, 1, EAR_IN));

    const det = clamp((k - .45) / .3);
    E.innerEars.setAttribute('opacity', det);
    E.details.setAttribute('opacity', det);
    E.face.setAttribute('transform', `translate(${h.x} ${h.y}) scale(${k})`);

    const open = Math.max(.08, st.eyeOpen);
    const eb = Math.max(1, 1 + (1 - k) * .6); // bigger eyes when the head is tiny
    vis(E.eyeL, !st.happy); vis(E.eyeR, !st.happy);
    vis(E.happyL, st.happy); vis(E.happyR, st.happy);
    E.eyeL.setAttribute('transform', `translate(-17 -4) scale(${eb} ${eb * open})`);
    E.eyeR.setAttribute('transform', `translate(17 -4) scale(${eb} ${eb * open})`);
  }

  // ---------- Speech bubble ----------
  const bubble = $('bubble'), bubbleRect = $('bubbleRect'), bubbleText = $('bubbleText'), bubbleTail = $('bubbleTail');
  let bubbleCur = '', bubbleW = 100;
  function bubbleAt(text, local, dur, head, side) {
    if (local < 0 || local > dur) return null;
    const x = head.x + (side > 0 ? 30 : -70), y = head.y - 120;
    return { text, x, y, headDx: head.x - x,
             s: easeOutBack(clamp(local / .25)), a: clamp(local / .08) * clamp((dur - local) / .25) };
  }
  function renderBubble(bb) {
    if (!bb) { bubble.setAttribute('opacity', 0); return; }
    if (bb.text !== bubbleCur) {
      bubbleText.textContent = bubbleCur = bb.text;
      bubbleW = bubbleText.getComputedTextLength() + 38;
      attrs(bubbleRect, { x: -bubbleW / 2, width: bubbleW });
    }
    const c = clamp(bb.headDx * .5, -bubbleW / 2 + 22, bubbleW / 2 - 22);
    const tip = clamp(bb.headDx * .7, -bubbleW / 2, bubbleW / 2);
    bubbleTail.setAttribute('d', `M${c - 10} 15 L${tip} 42 L${c + 10} 15`);
    bubble.setAttribute('transform', `translate(${bb.x} ${bb.y}) scale(${bb.s})`);
    bubble.setAttribute('opacity', bb.a);
  }

  // ---------- Sound-effect text ----------
  const fxEl = $('fx'); let fxCur = '';
  function popFx(text, local, dur, x, y, rot) {
    if (local < 0 || local > dur) return null;
    return { text, x, y: y - local * 18, rot, s: easeOutBack(clamp(local / .25)), a: clamp((dur - local) / .3) };
  }
  function renderFx(f) {
    if (!f) { fxEl.setAttribute('opacity', 0); return; }
    if (f.text !== fxCur) fxEl.textContent = fxCur = f.text;
    fxEl.setAttribute('transform', `translate(${f.x} ${f.y}) rotate(${f.rot}) scale(${f.s})`);
    fxEl.setAttribute('opacity', f.a);
  }

  // ---------- Sparkles ----------
  const STAR = "M0 -11 L2.8 -2.8 L11 0 L2.8 2.8 L0 11 L-2.8 2.8 L-11 0 L-2.8 -2.8 Z";
  const sparks = Array.from({ length: 7 }, (_, i) => {
    const p = document.createElementNS(NS, 'path');
    attrs(p, { d: STAR, fill: i % 2 ? '#ffd23f' : '#fff3a0', stroke: '#3b2314', 'stroke-width': 2, 'stroke-linejoin': 'round' });
    $('sparkles').appendChild(p);
    return p;
  });
  function renderSparks(tau, cx, cy) {
    sparks.forEach((p, i) => {
      const on = tau >= 0 && tau <= 1.4;
      vis(p, on);
      if (!on) return;
      const a = -Math.PI * .95 + (i / (sparks.length - 1)) * Math.PI * .9;
      const d = 75 + tau * 55;
      const s = Math.sin(Math.PI * clamp(tau / 1.4)) * (.8 + .4 * ((i * 37) % 5) / 5);
      p.setAttribute('transform', `translate(${cx + Math.cos(a) * d} ${cy + Math.sin(a) * d}) rotate(${tau * 120 + i * 20}) scale(${s})`);
    });
  }

  // ---------- Timeline ----------
  function frame(time) {
    let tt = time % TOTAL, i = 0;
    while (tt >= PHASES[i].d) { tt -= PHASES[i].d; i++; }
    const ph = PHASES[i].n, tau = tt, u = tau / PHASES[i].d;
    let st, bub = null, fx = null, spark = -1;
    const walkBob = env => -Math.abs(Math.sin(tau * 13)) * 5 * env;

    switch (ph) {
      case 'idle':
        st = restGeom(START_X, time);
        bub = bubbleAt('if I fits…', tau - .3, 1.4, st.head, 1);
        break;
      case 'walkTo': {
        const env = Math.sin(Math.PI * u);
        st = restGeom(lerp(START_X, APPROACH_X, smooth(u)), time, { bob: walkBob(env), walk: tau * 13, wAmp: 7 * env });
        break;
      }
      case 'squeeze':
        st = flowGeom(u, 0, time);
        fx = popFx('squish', tau - .15, .6, 395, 318, -8);
        break;
      case 'flow': {
        const s = FLOW_TOTAL * (.6 * u + .4 * smooth(u));
        st = flowGeom(1, s, time);
        fx = popFx('slurp!', (s - (L_CAT - 40)) / 290, .9, 360, 318, -6)
          || popFx('bloop!', (s - T) / 290, .9, PE.x + 40, 318, 8);
        break;
      }
      case 'celebrate': {
        const sq = .16 * Math.sin(tau * 15) * Math.exp(-tau * 3);
        const hop = (tau > 1.1 && tau < 1.55) ? -40 * Math.sin(Math.PI * (tau - 1.1) / .45) : 0;
        st = restGeom(FX, time, { sq, bob: hop, lift: hop });
        st.happy = tau > .8 && tau < 2.2;
        bub = bubbleAt('…I flows! ✨', tau - .35, 2.0, st.head, -1);
        spark = tau;
        break;
      }
      case 'walkOff': {
        const env = Math.min(1, u * 4);
        st = restGeom(lerp(FX, 1420, Math.pow(u, 1.4)), time,
          { bob: walkBob(env), walk: tau * 13, wAmp: 7 * env, tailAmp: 1 + .6 * env });
        break;
      }
      case 'walkIn': {
        const env = Math.min(1, (1 - u) * 4);
        st = restGeom(lerp(-240, START_X, easeOutCubic(u)), time,
          { bob: walkBob(env), walk: tau * 13, wAmp: 7 * env, tailAmp: 1 + .6 * env });
        break;
      }
    }

    render(st, time);
    renderBubble(bub);
    renderFx(fx);
    renderSparks(spark, FX + 20, FLOOR - 110);
    $('minHand').setAttribute('transform', `rotate(${time * 36})`);
    $('hourHand').setAttribute('transform', `rotate(${time * 3})`);
  }

  // ---------- Loop & controls ----------
  let simTime = 0, speed = 1, playing = true, last = performance.now();
  const playBtn = $('play');
  playBtn.onclick = () => { playing = !playing; playBtn.textContent = playing ? '⏸ Pause' : '▶ Play'; };
  document.querySelectorAll('[data-speed]').forEach(b => b.onclick = () => {
    speed = +b.dataset.speed;
    document.querySelectorAll('[data-speed]').forEach(x => x.classList.toggle('on', x === b));
  });
  $('restart').onclick = () => { simTime = 0; };
  addEventListener('keydown', e => { if (e.code === 'Space') { e.preventDefault(); playBtn.click(); } });

  function tick(now) {
    const dt = Math.min(.05, (now - last) / 1000);
    last = now;
    if (playing) simTime += dt * speed;
    frame(simTime);
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
</script>
</body>
</html>
```

**What happens in one loop (about 17 seconds):**
1. **Idle:** the cat sits, blinks and wags its tail, and says *"if I fits…"*
2. **Squeeze:** it walks to the funnel, and its head shrinks and squishes into the opening.
3. **Flow:** the body melts into a puddle and drains into the tube, and the tail slurps in last. Inside the tube the cat is a stream with bulges moving along it. Its tiny head, with big eyes and little ears, leads the way over the humps.
4. **Re-form:** the head pops out of the nozzle (*"bloop!"*), and the body refills behind it. Then the paws pop out and the tail springs up.
5. **Celebrate:** the cat wobbles, does a happy-eyed hop with sparkles, and says *"…I flows! ✨"* Then it walks off to the right and comes back in from the left.

**Things you can easily tweak:**
- **`D`:** the tube's path. Change it to any SVG path and the cat will follow it automatically.
- **`L_CAT`:** how long the cat stretches inside the tube.
- **`stdDeviation` and the color-matrix values in `#goo`:** control how "gooey" the cat looks. More blur makes the shapes merge more.
- **Cat color:** set by `#f59e42`. Change every occurrence of it.

The controls let you pause, restart, and switch between 0.5×, 1× and 2× speed. The spacebar also toggles pause.