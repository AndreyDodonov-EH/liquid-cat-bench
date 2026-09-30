Here’s a self-contained HTML animation—no libraries or renderer needed. The cat’s SVG outline continuously deforms, gets squeezed inside the tube, and reforms on the other side.

Save this as **`liquid-cat.html`** and open it in a browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cats Are Liquid</title>

<style>
  :root {
    color-scheme: light;
    font-family: ui-rounded, "SF Pro Rounded", system-ui, sans-serif;
    color: #49382e;
    background: #faf5ee;
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 24px;
    background:
      radial-gradient(ellipse at 20% 15%, #ffecd5, transparent 55%),
      radial-gradient(ellipse at 90% 85%, #e7eaf8, transparent 50%),
      #faf5ee;
  }

  .card {
    width: min(960px, 100%);
    overflow: hidden;
    border: 1px solid #fff;
    border-radius: 28px;
    background: #fffdf8;
    box-shadow:
      0 24px 80px #59453512,
      0 3px 12px #59453508;
  }

  header {
    padding: 30px 34px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
  }

  h1 {
    margin: 0;
    font-size: clamp(24px, 4vw, 36px);
    letter-spacing: -1.3px;
  }

  .subtitle {
    margin: 7px 0 0;
    color: #948273;
    font-size: 14px;
  }

  .badge {
    padding: 8px 12px;
    border-radius: 100px;
    background: #fff0d6;
    color: #a87731;
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 1px;
    white-space: nowrap;
  }

  svg {
    width: 100%;
    display: block;
    overflow: hidden;
  }

  .diagram-label {
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 700;
    fill: #a19689;
    text-anchor: middle;
  }

  .controls {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 30px 24px;
    flex-wrap: wrap;
  }

  button {
    border: 1px solid #e9e0d5;
    border-radius: 12px;
    background: #fff;
    color: #665041;
    padding: 10px 15px;
    font: inherit;
    font-size: 13px;
    cursor: pointer;
  }

  button:hover { background: #fff4e5; }
  button:focus-visible, input:focus-visible {
    outline: 3px solid #e0b36c;
    outline-offset: 3px;
  }

  .speed {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-left: auto;
    color: #948273;
    font-size: 12px;
  }

  input {
    width: 95px;
    accent-color: #e8a74a;
  }

  output {
    min-width: 30px;
    font-variant-numeric: tabular-nums;
  }

  .progress {
    height: 4px;
    background: #f2ebe1;
  }

  .progress > div {
    height: 100%;
    width: 0;
    background: #e9ad55;
  }

  @media (max-width: 520px) {
    body { padding: 12px; }
    header { padding: 22px 22px 0; }
    .badge { display: none; }
    .controls { padding: 0 18px 20px; }
    .speed { gap: 6px; }
    input { width: 70px; }
  }
</style>
</head>

<body>
<main class="card">
  <header>
    <div>
      <h1>Cats are liquid.</h1>
      <p class="subtitle">A small experiment in feline fluid dynamics.</p>
    </div>
    <span class="badge">100% SVG + JS</span>
  </header>

  <svg viewBox="0 0 900 410"
       role="img"
       aria-labelledby="svgTitle svgDescription">
    <title id="svgTitle">A liquid cartoon cat</title>
    <desc id="svgDescription">
      An orange cat squeezes into a narrow glass tube,
      flows through it like liquid, and reforms on the other side.
    </desc>

    <defs>
      <linearGradient id="fur" x1="0" y1="0" x2="0.2" y2="1">
        <stop offset="0" stop-color="#ffc76a"/>
        <stop offset="1" stop-color="#f4a348"/>
      </linearGradient>

      <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#d7eff8" stop-opacity=".6"/>
        <stop offset=".45" stop-color="#edf8fc" stop-opacity=".1"/>
        <stop offset="1" stop-color="#a7cbdc" stop-opacity=".35"/>
      </linearGradient>

      <filter id="blur">
        <feGaussianBlur stdDeviation="5"/>
      </filter>
    </defs>

    <!-- Background and workbench -->
    <ellipse cx="450" cy="246" rx="367" ry="130"
             fill="#fcf6eb"/>

    <path d="M70 324H830"
          stroke="#e8ded0" stroke-width="2" stroke-linecap="round"/>

    <text x="190" y="365" class="diagram-label">SOLID-ISH</text>
    <text x="450" y="365" class="diagram-label">SQUEEZE ZONE</text>
    <text x="730" y="365" class="diagram-label">CAT, AGAIN</text>

    <text id="phase" x="450" y="91"
          text-anchor="middle"
          fill="#a58b6b"
          font-size="15"
          font-style="italic">An ordinary cat. Mostly.</text>

    <!-- Tube supports -->
    <g fill="#dbe3e6" stroke="#b5c5cc" stroke-width="2">
      <path d="M348 275V316H338V323H375V316H365V275Z"/>
      <path d="M535 275V316H525V323H562V316H552V275Z"/>
    </g>

    <!-- Rear of glass tube -->
    <g>
      <rect x="310" y="226" width="280" height="48"
            fill="url(#glass)"/>
      <ellipse cx="310" cy="250" rx="9" ry="24"
               fill="#d8edf5" fill-opacity=".25"
               stroke="#a4c3d2" stroke-width="2"/>
      <ellipse cx="590" cy="250" rx="9" ry="24"
               fill="#d8edf5" fill-opacity=".25"
               stroke="#a4c3d2" stroke-width="2"/>
    </g>

    <ellipse id="shadow" cx="190" cy="321" rx="62" ry="7"
             fill="#9c7149" opacity=".16" filter="url(#blur)"/>

    <!-- The entire cat is animated procedurally. -->
    <g id="cat">
      <path id="tail"
            fill="none" stroke="#784528" stroke-width="19"
            stroke-linecap="round"/>
      <path id="tailInner"
            fill="none" stroke="#ef9e42" stroke-width="12"
            stroke-linecap="round"/>

      <path id="body"
            fill="url(#fur)" stroke="#784528"
            stroke-width="3.5"
            stroke-linejoin="round"/>

      <g id="details">
        <path d="M-42-73L-24-61L-39-48Z
                 M42-73L24-61L39-48Z"
              fill="#e98d71"/>

        <g stroke="#d18a3b" stroke-width="5" stroke-linecap="round">
          <path d="M-12-63L-8-49"/>
          <path d="M0-66V-51"/>
          <path d="M12-63L8-49"/>
        </g>

        <g fill="none" stroke="#b77735"
           stroke-width="2.5" stroke-linecap="round">
          <path d="M-29 43Q-22 51-15 43"/>
          <path d="M15 43Q22 51 29 43"/>
        </g>
      </g>

      <g id="face">
        <g id="eyes">
          <ellipse cx="-20" cy="-5" rx="10" ry="12" fill="#fffdf7"/>
          <ellipse cx="20" cy="-5" rx="10" ry="12" fill="#fffdf7"/>
          <ellipse cx="-18" cy="-4" rx="3.7" ry="6" fill="#563b2b"/>
          <ellipse cx="22" cy="-4" rx="3.7" ry="6" fill="#563b2b"/>
          <circle cx="-17" cy="-6" r="1.4" fill="white"/>
          <circle cx="23" cy="-6" r="1.4" fill="white"/>
        </g>

        <g id="closedEyes" fill="none" stroke="#784528"
           stroke-width="2.5" stroke-linecap="round" opacity="0">
          <path d="M-29-4Q-20 2-11-4"/>
          <path d="M11-4Q20 2 29-4"/>
        </g>

        <ellipse cx="-34" cy="11" rx="8" ry="4"
                 fill="#ed8d72" opacity=".45"/>
        <ellipse cx="34" cy="11" rx="8" ry="4"
                 fill="#ed8d72" opacity=".45"/>

        <path d="M-4 9Q0 6 4 9L0 13Z" fill="#975244"/>
        <path d="M0 13V16M0 16Q-6 23-11 17M0 16Q6 23 11 17"
              fill="none" stroke="#784528"
              stroke-width="2" stroke-linecap="round"/>

        <g id="whiskers" stroke="#975e32"
           stroke-width="1.7" stroke-linecap="round">
          <path d="M-35 3L-54-1M-35 12L-56 14"/>
          <path d="M35 3L54-1M35 12L56 14"/>
        </g>
      </g>
    </g>

    <!-- Front glass stays above the cat. -->
    <g fill="none" stroke-linecap="round">
      <path d="M310 226H590M310 274H590"
            stroke="#9fbdcd" stroke-width="2.5"/>
      <path d="M322 231H578"
            stroke="white" stroke-width="3" opacity=".8"/>
      <path d="M322 269H578"
            stroke="#c2dde9" stroke-width="1" opacity=".8"/>
      <ellipse cx="310" cy="250" rx="9" ry="24"
               stroke="#a4c3d2" stroke-width="2"/>
      <ellipse cx="590" cy="250" rx="9" ry="24"
               stroke="#a4c3d2" stroke-width="2"/>
    </g>

    <!-- Little direction marks -->
    <g fill="none" stroke="#d4c6b2"
       stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M271 351H286M281 346L286 351L281 356"/>
      <path d="M614 351H629M624 346L629 351L624 356"/>
    </g>
  </svg>

  <div class="controls">
    <button id="play" type="button">Pause</button>
    <button id="replay" type="button">↻ Replay</button>

    <label class="speed">
      Speed
      <input id="speed" type="range"
             min="0.5" max="2" value="1" step="0.25">
      <output id="speedValue">1×</output>
    </label>
  </div>

  <div class="progress"><div id="progress"></div></div>
</main>

<script>
(() => {
  const $ = id => document.getElementById(id);
  const body = $("body");
  const cat = $("cat");
  const face = $("face");
  const details = $("details");
  const tail = $("tail");
  const tailInner = $("tailInner");
  const shadow = $("shadow");

  const duration = 10.2;
  let time = 0;
  let speed = 1;
  let playing = !matchMedia("(prefers-reduced-motion: reduce)").matches;
  let previous = null;
  let lastPhase = "";

  const clamp = (n, a = 0, b = 1) => Math.max(a, Math.min(b, n));
  const mix = (a, b, t) => a + (b - a) * t;
  const smooth = t => {
    t = clamp(t);
    return t * t * (3 - 2 * t);
  };
  const ramp = (a, b, x) => smooth((x - a) / (b - a));

  /*
   * Clockwise contour of a plump cat.
   * Its ears are part of the silhouette, so they melt too.
   */
  const anchors = [
    [-58, 15], [-53, -26], [-45, -45], [-49, -87],
    [-19, -63], [0, -68], [19, -63], [49, -87],
    [45, -45], [53, -26], [58, 15], [50, 48],
    [28, 65], [0, 69], [-28, 65], [-50, 48]
  ];

  // Sample a closed Catmull–Rom spline once.
  const contour = [];
  const n = anchors.length;

  for (let i = 0; i < n; i++) {
    const p0 = anchors[(i - 1 + n) % n];
    const p1 = anchors[i];
    const p2 = anchors[(i + 1) % n];
    const p3 = anchors[(i + 2) % n];

    for (let j = 0; j < 16; j++) {
      const t = j / 16;
      const t2 = t * t;
      const t3 = t2 * t;

      const point = [0, 1].map(axis =>
        0.5 * (
          2 * p1[axis] +
          (-p0[axis] + p2[axis]) * t +
          (2*p0[axis] - 5*p1[axis] + 4*p2[axis] - p3[axis]) * t2 +
          (-p0[axis] + 3*p1[axis] - 3*p2[axis] + p3[axis]) * t3
        )
      );

      contour.push({
        x: point[0],
        y: point[1],
        angle: Math.atan2(point[1], point[0])
      });
    }
  }

  // Timeline: [seconds, horizontal position, fluid amount].
  const keys = [
    [0,    190, 0],
    [1.1,  190, 0],
    [2.15, 270, 0.22],
    [3.5,  433, 1],
    [4.65, 480, 1],
    [6.1,  651, 0.55],
    [7.25, 730, 0],
    [9.65, 730, 0],
    [9.66, 190, 0],
    [10.2, 190, 0]
  ];

  function stateAt(t) {
    for (let i = 0; i < keys.length - 1; i++) {
      const a = keys[i], b = keys[i + 1];
      if (t >= a[0] && t <= b[0]) {
        const u = smooth((t - a[0]) / (b[0] - a[0]));
        return {
          x: mix(a[1], b[1], u),
          fluid: mix(a[2], b[2], u)
        };
      }
    }
    return { x: 190, fluid: 0 };
  }

  /*
   * Spatial constriction:
   * every contour sample inside the tube is compressed to fit.
   * Smooth transitions at the openings avoid snapping.
   */
  function squeezeY(x, offset) {
    const inside =
      ramp(301, 324, x) * (1 - ramp(576, 599, x));

    const confined = 17.5 * Math.tanh(offset / 17.5);
    return mix(offset, confined, inside);
  }

  function draw(t) {
    const { x: cx, fluid: f } = stateAt(t);

    const breath = Math.sin(t * 3.1) * 1.5 * (1 - f);
    const cy = 250;
    const halfLength = 135;
    const liquidHeight = 15.5 + Math.sin(t * 5) * 0.7;

    let d = "";

    contour.forEach((p, i) => {
      const liquidX = Math.cos(p.angle) * halfLength;
      const liquidY = Math.sin(p.angle) * liquidHeight;

      const px = cx + mix(p.x, liquidX, f);
      const localY = mix(p.y + breath, liquidY, f);
      const py = cy + squeezeY(px, localY);

      d += `${i ? "L" : "M"}${px.toFixed(2)},${py.toFixed(2)}`;
    });

    body.setAttribute("d", d + "Z");

    // Subtle disappearing/reappearing transition at the loop boundary.
    let opacity = 1 - ramp(9.1, 9.6, t);
    if (t >= 9.66) opacity = ramp(9.7, 10.2, t);
    cat.setAttribute("opacity", opacity);

    // The face rides with the liquid rather than remaining behind.
    const faceY = cy + squeezeY(cx, mix(-25 + breath, -1, f));
    face.setAttribute(
      "transform",
      `translate(${cx},${faceY}) scale(${mix(1, 0.93, f)},${mix(1, 0.58, f)})`
    );

    $("whiskers").setAttribute("opacity", 1 - f * 0.85);

    // Small details disappear before the cat becomes fully liquid.
    details.setAttribute("transform", `translate(${cx},${cy + breath})`);
    details.setAttribute("opacity", clamp(1 - f * 4));

    const tailOpacity = clamp(1 - f * 2.7);
    const wag = Math.sin(t * 4.5) * 7;
    const tailPath = `
      M ${cx - 45} ${cy + 42}
      C ${cx - 92} ${cy + 52},
        ${cx - 99} ${cy + 8},
        ${cx - 83 + wag} ${cy - 6}
    `;

    tail.setAttribute("d", tailPath);
    tailInner.setAttribute("d", tailPath);
    tail.setAttribute("opacity", tailOpacity);
    tailInner.setAttribute("opacity", tailOpacity);

    // Blink before and after the journey.
    const blink =
      (t > 0.64 && t < 0.79) ||
      (t > 8.08 && t < 8.25);

    $("eyes").setAttribute("opacity", blink ? 0 : 1);
    $("closedEyes").setAttribute("opacity", blink ? 1 : 0);

    shadow.setAttribute("cx", cx);
    shadow.setAttribute("rx", mix(62, 115, f));
    shadow.setAttribute("opacity", 0.16 * (1 - f) * opacity);

    const phase =
      t < 1.5 ? "An ordinary cat. Mostly." :
      t < 3.4 ? "If I fits…" :
      t < 5.15 ? "…I flows." :
      t < 7.25 ? "Reassembling the cat…" :
      "No bones? No problem.";

    if (phase !== lastPhase) {
      $("phase").textContent = phase;
      lastPhase = phase;
    }

    $("progress").style.width = `${t / duration * 100}%`;
  }

  function updatePlayButton() {
    $("play").textContent = playing ? "Pause" : "Play";
    $("play").setAttribute("aria-label", playing ? "Pause animation" : "Play animation");
  }

  $("play").addEventListener("click", () => {
    playing = !playing;
    updatePlayButton();
  });

  $("replay").addEventListener("click", () => {
    time = 0;
    playing = true;
    updatePlayButton();
    draw(time);
  });

  $("speed").addEventListener("input", event => {
    speed = Number(event.target.value);
    $("speedValue").textContent = `${speed}×`;
  });

  // Avoid jumping forward after the browser tab was hidden.
  document.addEventListener("visibilitychange", () => {
    previous = null;
  });

  function frame(now) {
    if (previous !== null && playing && !document.hidden) {
      const dt = Math.min((now - previous) / 1000, 0.05);
      time = (time + dt * speed) % duration;
    }

    previous = now;
    draw(time);
    requestAnimationFrame(frame);
  }

  updatePlayButton();
  draw(0);
  requestAnimationFrame(frame);
})();
</script>
</body>
</html>
```