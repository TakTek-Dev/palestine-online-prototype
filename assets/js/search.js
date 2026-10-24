// Search every entry on the board: words, names, places, desks. Results update as you type.
(() => {
  const form = document.querySelector('.search-box');
  if (!form) return;
  const q = form.querySelector('#q'), list = document.querySelector('.results'), count = document.querySelector('.s-count');
  const chips = [...form.querySelectorAll('.f-chip')];
  const DESK = Object.fromEntries(chips.map((c) => [c.dataset.desk, c.textContent]));
  const CHIP = JSON.parse(document.getElementById('chips').textContent);
  const fold = (s) => s.toLowerCase().normalize('NFD').replace(/\p{M}/gu, '').replace(/[‘’'`]/g, '').replace(/[-–—]/g, ' ');
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let data = [], desk = null;
  const params = new URLSearchParams(location.search);
  q.value = params.get('q') || '';

  const mark = (text, terms) => {
    let out = esc(text);
    for (const t of terms) {
      if (t.length < 2) continue;
      out = out.replace(new RegExp(`(${t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'), '<mark>$1</mark>');
    }
    return out;
  };
  const day = (iso) => new Date(iso + 'T12:00:00Z').toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' });

  function run() {
    const terms = fold(q.value.trim()).split(/\s+/).filter(Boolean);
    const hits = data.filter((d) => (!desk || d.k === desk) && terms.every((t) => d._t.includes(t)))
      .map((d) => ({ d, score: terms.reduce((s, t) => s + (fold(d.t).includes(t) ? 3 : 0) + (fold(d.n + ' ' + d.p).includes(t) ? 2 : 0), 0) }))
      .sort((a, b) => b.score - a.score || b.d.d.localeCompare(a.d.d));
    count.textContent = terms.length || desk ? `${hits.length} ${hits.length === 1 ? 'entry' : 'entries'}` : `${data.length} entries. Type to narrow them down.`;
    const words = q.value.trim().split(/\s+/).filter(Boolean);
    list.innerHTML = hits.map(({ d }) => `<li class="res"><a href="report/${d.id}.html">
      ${d.img ? `<img src="assets/img/photo/${d.img}.webp" alt="" loading="lazy" width="160" height="107">` : '<span class="res-ph" aria-hidden="true"></span>'}
      <span class="res-t"><span class="res-m">${CHIP[d.st]}<span class="desk">${esc(DESK[d.k] || '')}</span><time>${day(d.d)}</time></span>
      <b>${mark(d.t, words)}</b><span class="res-s">${mark(d.s, words)}</span></span></a></li>`).join('');
    const u = new URL(location.href);
    if (q.value) u.searchParams.set('q', q.value); else u.searchParams.delete('q');
    history.replaceState(null, '', u);
  }
  form.addEventListener('submit', (e) => { e.preventDefault(); run(); });
  q.addEventListener('input', run);
  chips.forEach((c) => c.addEventListener('click', () => {
    desk = desk === c.dataset.desk ? null : c.dataset.desk;
    chips.forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.desk === desk)));
    run();
  }));
  fetch('assets/data/search.json').then((r) => r.json()).then((j) => {
    data = j.map((d) => ({ ...d, _t: fold([d.t, d.s, d.p, d.n, DESK[d.k] || ''].join(' ')) }));
    run();
  });
})();
