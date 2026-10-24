// Palestine Online: theme switch, the net's knots, reveals.
(() => {
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- day / night
  const dark = () => root.dataset.theme === 'night' || (root.dataset.theme === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);
  const label = () => document.querySelectorAll('[data-theme-toggle]').forEach((b) => b.setAttribute('aria-label', dark() ? 'Switch to day' : 'Switch to night'));
  label();
  document.addEventListener('click', (e) => {
    const b = e.target.closest('[data-theme-toggle]');
    if (!b) return;
    const next = dark() ? 'day' : 'night';
    const go = () => { root.dataset.theme = next; try { localStorage.setItem('po-theme', next); } catch (_) {} label(); };
    if (document.startViewTransition && !reduce) document.startViewTransition(go); else go();
  });

  // ---- share: the system sheet on phones, the clipboard elsewhere
  document.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-share]');
    if (!b) return;
    const url = location.href.split('#')[0], title = document.title;
    const label = b.querySelector('span');
    try {
      if (navigator.share && matchMedia('(pointer: coarse)').matches) { await navigator.share({ title, url }); return; }
      await navigator.clipboard.writeText(url);
      b.classList.add('done'); label.textContent = 'Link copied';
      setTimeout(() => { b.classList.remove('done'); label.textContent = 'Copy the link'; }, 2400);
    } catch (_) { /* cancelled or blocked */ }
  });

  // ---- first visit: the hash turns into a net cell, the net is cast, one knot answers
  const ready = () => document.dispatchEvent(new Event('po:ready'));
  const loader = document.getElementById('loader');
  if (loader && root.classList.contains('js-loading')) {
    const mark = loader.querySelector('.ld-mark');
    const netSvg = loader.querySelector('.ld-net');
    let done = false;
    const finish = () => {
      if (done) return; done = true;
      root.classList.remove('js-loading');
      try { sessionStorage.setItem('po-cast', '1'); } catch (_) {}
      ready();
    };
    const W = innerWidth, H = innerHeight, cx = W / 2, cy = H / 2;
    const s = parseFloat(getComputedStyle(mark).width) / mark.viewBox.baseVal.width;   // px per mark unit
    const G = 17 * s, P = 34 * s, R = Math.hypot(W, H);
    let d = '', segs = [];
    for (let k = 0; G + k * P < R; k++) {
      for (const p of [G + k * P, -G - k * P]) {
        segs.push([p, 0, p, -R], [p, 0, p, R], [0, p, -R, p], [0, p, R, p]);
      }
    }
    netSvg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    netSvg.innerHTML = `<g transform="translate(${cx} ${cy}) rotate(45)">` +
      segs.map(([x1, y1, x2, y2]) => `<path d="M${x1.toFixed(1)} ${y1.toFixed(1)}L${x2.toFixed(1)} ${y2.toFixed(1)}" pathLength="1" style="stroke-dasharray:1;stroke-dashoffset:1"/>`).join('') + '</g>';
    requestAnimationFrame(() => {
      loader.classList.add('ld-go');
      netSvg.querySelectorAll('path').forEach((el, i) => {
        const [x1, y1] = segs[i];
        const dist = Math.abs(x1 || y1);
        el.animate([{ strokeDashoffset: 1 }, { strokeDashoffset: 0 }],
          { duration: 650, delay: 440 + dist * 0.35, easing: 'cubic-bezier(.3,.7,.3,1)', fill: 'forwards' });
      });
      setTimeout(() => {
        const target = document.querySelector('.mast .brand .mark');
        loader.classList.add('ld-fly');
        setTimeout(() => loader.classList.add('ld-out'), 180);
        if (target) {
          const a = mark.getBoundingClientRect(), b = target.getBoundingClientRect();
          if (b.bottom > 0) {
            const k = b.width / a.width;
            mark.animate([{ transform: 'none' },
              { transform: `translate(${b.left + b.width / 2 - (a.left + a.width / 2)}px, ${b.top + b.height / 2 - (a.top + a.height / 2)}px) scale(${k})` }],
              { duration: 480, easing: 'cubic-bezier(.65,0,.25,1)', fill: 'forwards' });
          } else mark.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 300, fill: 'forwards' });
        }
        setTimeout(finish, 520);
      }, 1150);
    });
    loader.addEventListener('click', finish);
    addEventListener('keydown', finish, { once: true });
    setTimeout(finish, 5000);
  } else {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready); else setTimeout(ready);
  }

  // ---- the hero net: shown whole, then torn to today's count; answering knots ping
  document.addEventListener('po:ready', () => {
    document.querySelectorAll('svg.net').forEach((svg) => {
      const tear = () => setTimeout(() => svg.classList.add('torn'), reduce ? 0 : 120);
      if (reduce) { svg.classList.add('torn'); return; }
      const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); tear(); } }, { threshold: .25 });
      io.observe(svg);
      const lit = [...svg.querySelectorAll('.k.lit')];
      if (!lit.length) return;
      let n = 0;
      setInterval(() => {
        if (document.hidden || !svg.classList.contains('torn')) return;
        const k = lit[(n++ * 3) % lit.length];
        const r = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        r.setAttribute('d', k.getAttribute('d')); r.setAttribute('class', 'ping');
        svg.appendChild(r); setTimeout(() => r.remove(), 1700);
      }, 1500);
    });
  }, { once: true });

  // ---- the net, redrawn for any day of the month (same lattice as tools/net.py).
  // With `cols` it is rebuilt from scratch, knots and all, for a narrower screen.
  function knit(svg, routed, answering, cols) {
    const n = +svg.dataset.prewar, DX = +svg.dataset.dx, DY = DX / 2;
    const C = cols || +svg.dataset.cols;
    const pt = (i) => { const r = Math.floor(i / C), c = i % C; return [c * DX + (r % 2) * DX / 2 + DX / 2, r * DY + DY]; };
    const nb = (i) => {
      const r = Math.floor(i / C), c = i % C;
      return (r % 2 === 0 ? [[r + 1, c - 1], [r + 1, c]] : [[r + 1, c], [r + 1, c + 1]])
        .filter(([rr, cc]) => cc >= 0 && cc < C && rr * C + cc < n).map(([rr, cc]) => rr * C + cc);
    };
    const lit = new Set();
    if (answering) { const step = routed / answering; for (let k = 0; k < answering; k++) lit.add(Math.floor(step * k + step * 0.5)); }
    const kind = (i) => (lit.has(i) ? 'lit' : i < routed ? 'held' : 'gone');
    let held = '', ghost = '', fray = '';
    for (let i = 0; i < n; i++) {
      const [x, y] = pt(i);
      for (const j of nb(i)) {
        const [x2, y2] = pt(j), seg = `M${x} ${y}L${x2} ${y2}`;
        if (i < routed && j < routed) held += seg;
        else {
          ghost += seg;
          if (i < routed) fray += `M${x} ${y}Q${(x + (x2 - x) * .3).toFixed(1)} ${(y + (y2 - y) * .45).toFixed(1)} ${(x + (x2 - x) * .55).toFixed(1)} ${(y + (y2 - y) * .55 + 2.5).toFixed(1)}`;
        }
      }
    }
    const rows = Math.ceil(n / C), W = C * DX + DX / 2, H = rows * DY + DY, edge = Math.floor(routed / C);
    if (cols && cols !== +svg.dataset.cols) {
      svg.dataset.cols = C;
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
      let g = '';
      for (let r = 0; r < rows; r++) {
        g += `<g class="nr" style="--d:${Math.max(0, r - edge)}">`;
        for (let i = r * C; i < Math.min(n, (r + 1) * C); i++) {
          const [x, y] = pt(i);
          g += `<path class="k ${kind(i)}" d="M${x} ${y - 4.2}l4.2 4.2-4.2 4.2-4.2-4.2z" data-x="${x}" data-y="${y}" data-i="${i}"/>`;
        }
        g += '</g>';
      }
      svg.querySelector('.knots').innerHTML = g;
    } else {
      svg.querySelectorAll('.k').forEach((k) => k.setAttribute('class', 'k ' + kind(+k.dataset.i)));
    }
    svg.querySelector('.held').setAttribute('d', held);
    svg.querySelector('.fray').setAttribute('d', fray);
    svg.querySelector('.ghost').setAttribute('d', ghost);
    svg.querySelector('.was').setAttribute('d', ghost);
    svg.dataset.routed = routed; svg.dataset.answering = answering;
    const note = svg.querySelector('.gone-note');
    if (note) {
      note.querySelector('.gn-n').textContent = n - routed;
      note.setAttribute('transform', `translate(${W / 2} ${Math.round(((edge + 1) * DY + DY + H) / 2 + 8)})`);
    }
  }

  // phones get a taller, narrower net so the knots stay big enough to read
  const narrow = matchMedia('(max-width: 760px)');
  const fit = () => document.querySelectorAll('svg.net[data-days], svg.net.fit').forEach((svg) => {
    const want = narrow.matches ? 22 : 32;
    if (+svg.dataset.cols !== want) knit(svg, +svg.dataset.routed, +svg.dataset.answering, want);
  });
  fit();
  narrow.addEventListener('change', fit);

  document.querySelectorAll('[data-scrub]').forEach((box) => {
    const svg = box.closest('.lead-net, .desk-net, .plate-knots').querySelector('svg.net');
    const days = JSON.parse(svg.dataset.days || '[]');
    const input = box.querySelector('input'), out = box.querySelector('output');
    const fmt = (iso) => { const d = new Date(iso + 'T12:00:00Z'); return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', timeZone: 'UTC' }); };
    const pre = +svg.dataset.prewar;
    const show = () => {
      const [iso, r, a] = days[+input.value];
      out.textContent = `${fmt(iso)} · ${r} of ${pre} routed · ${a} answering`;
      input.setAttribute('aria-valuetext', out.textContent);
      knit(svg, r, a);
    };
    input.addEventListener('input', show);
  });

  // ---- on phones a long group shows three rows until asked for the rest
  document.querySelectorAll('.group').forEach((g) => {
    const b = g.querySelector('.unfold');
    if (!b) return;
    g.classList.add('folded'); b.hidden = false;
    b.addEventListener('click', () => { g.classList.remove('folded'); b.setAttribute('aria-expanded', 'true'); });
  });

  // ---- rows and charts arrive as they come into view
  const seen = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); seen.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.row, .big-chart').forEach((el) => (reduce ? el.classList.add('in') : seen.observe(el)));

  // ---- the net: name the knot under the pointer
  document.querySelectorAll('svg.net').forEach((svg) => {
    const fig = svg.closest('.net-frame');
    const tip = fig && fig.querySelector('.net-tip');
    if (!tip) return;
    const prewar = +svg.dataset.prewar;
    let hot = null;
    const off = () => { if (hot) hot.classList.remove('hot'); hot = null; tip.classList.remove('on'); };
    svg.addEventListener('pointermove', (e) => {
      const knots = svg.querySelectorAll('.k');
      const box = svg.getBoundingClientRect();
      const vb = svg.viewBox.baseVal;
      const sx = (e.clientX - box.left) / box.width * vb.width, sy = (e.clientY - box.top) / box.height * vb.height;
      let best = null, bd = 1e9;
      for (const k of knots) {
        const x = +k.dataset.x, y = +k.dataset.y;
        const dd = (x - sx) ** 2 + (y - sy) ** 2;
        if (dd < bd) { bd = dd; best = k; }
      }
      if (!best || bd > 160) return off();
      if (best !== hot) {
        if (hot) hot.classList.remove('hot');
        hot = best; hot.classList.add('hot');
        const i = +best.dataset.i;
        const state = best.classList.contains('lit') ? 'routed, answering' : (i < +svg.dataset.routed ? 'routed, silent' : 'not routed');
        tip.textContent = `Block ${i + 1} of ${prewar} · ${state}`;
      }
      const fb = fig.getBoundingClientRect(), kb = best.getBoundingClientRect();
      tip.style.left = (kb.left + kb.width / 2 - fb.left) + 'px';
      tip.style.top = (kb.top - fb.top) + 'px';
      tip.classList.add('on');
    });
    svg.addEventListener('pointerleave', off);
  });
})();
