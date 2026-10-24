// The identity book: the cover net, and the chapter list that follows the reader.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const svg = document.querySelector('.bk-lattice');
  const mark = document.querySelector('.bk-mark');
  if (svg && mark) {
    const draw = () => {
      const box = svg.getBoundingClientRect(), m = mark.getBoundingClientRect();
      const s = m.width / mark.viewBox.baseVal.width;
      const cx = m.left - box.left + m.width / 2, cy = m.top - box.top + m.height / 2;
      const G = 17 * s, P = 34 * s, R = Math.hypot(box.width, box.height) * 1.2;
      let d = '';
      for (let k = 0; G + k * P < R; k++) for (const p of [G + k * P, -G - k * P]) d += `M${p} ${-R}V${R}M${-R} ${p}H${R}`;
      svg.setAttribute('viewBox', `0 0 ${box.width} ${box.height}`);
      svg.innerHTML = `<g transform="translate(${cx} ${cy}) rotate(45)"><path d="${d}"/></g>`;
    };
    draw();
    addEventListener('resize', draw);
    if (!reduce) svg.classList.add('cast');
  }
  const links = [...document.querySelectorAll('.bk-toc a[href^="#"]')];
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => {
      if (!e.isIntersecting) return;
      links.forEach((a) => a.toggleAttribute('aria-current', a.hash === '#' + e.target.id));
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  document.querySelectorAll('.ch').forEach((c) => io.observe(c));
})();
