(() => {
  const $ = (s, c = document) => c.querySelector(s), $$ = (s, c = document) => [...c.querySelectorAll(s)];

  // navigácia
  const nav = $('#nav');
  const onNav = () => nav.classList.toggle('is-solid', scrollY > 40);
  addEventListener('scroll', onNav, { passive: true }); onNav();
  const burger = $('#burger');
  burger.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    burger.setAttribute('aria-expanded', open); document.body.style.overflow = open ? 'hidden' : '';
  });
  $$('#menu a').forEach(a => a.addEventListener('click', () => { nav.classList.remove('is-open'); burger.setAttribute('aria-expanded', false); document.body.style.overflow = ''; }));

  // reveal
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -8% 0px' });
  $$('.rv, .clip').forEach(el => {
    const sib = el.parentElement ? [...el.parentElement.children].filter(c => c.classList.contains('rv')) : [];
    const idx = sib.indexOf(el); if (idx > 0) el.style.transitionDelay = Math.min(idx % 6, 5) * 0.07 + 's';
    io.observe(el);
  });

  // počítadlá v hero
  const fmt = (n, sep) => sep ? String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : String(n);
  const cio = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return; cio.unobserve(e.target);
    const el = e.target, to = +el.dataset.count, sep = el.hasAttribute('data-sep'), t0 = performance.now() + 1300, d = 1600;
    const step = t => { const p = Math.max(0, Math.min(1, (t - t0) / d)); el.textContent = fmt(Math.round(to * (1 - Math.pow(1 - p, 4))), sep); if (p < 1) requestAnimationFrame(step); };
    el.textContent = '0'; requestAnimationFrame(step);
  }), { threshold: .5 });
  $$('[data-count]').forEach(el => cio.observe(el));

  // magnetické tlačidlá
  if (matchMedia('(hover:hover)').matches) $$('.mag').forEach(b => {
    b.addEventListener('mousemove', e => { const r = b.getBoundingClientRect(); b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .16}px,${(e.clientY - r.top - r.height / 2) * .28}px)`; });
    b.addEventListener('mouseleave', () => { b.style.transform = ''; });
  });

  // 45 dní – časová os podľa scrollu
  const sec = $('#postup'), den = $('#den'), kroky = $$('.krok'), segs = $$('.seg'), zab = $$('#zabery img');
  if (sec) {
    const N = kroky.length; let last = -1, lastDay = -1, ticking = false;
    const update = () => {
      ticking = false;
      const r = sec.getBoundingClientRect(), span = sec.offsetHeight - innerHeight;
      if (r.bottom < 0 || r.top > innerHeight) return;
      const p = Math.max(0, Math.min(.9999, -r.top / span));
      const s = Math.floor(p * N), t = p * N - s, k = kroky[s];
      const od = +k.dataset.od, dd = +k.dataset.do;
      const day = s === N - 1 ? 45 : Math.round(od + t * (dd - od));
      if (day !== lastDay) { den.textContent = day; lastDay = day; }
      segs.forEach((g, i) => { const f = i < s ? 1 : i === s ? t : 0; g.style.setProperty('--f', f.toFixed(3)); g.classList.toggle('is-full', f > .55); });
      if (s !== last) {
        last = s;
        kroky.forEach((x, i) => { x.classList.toggle('is-on', i === s); x.classList.toggle('is-done', i < s); });
        zab.forEach((z, i) => z.classList.toggle('is-on', i === s));
      }
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    addEventListener('resize', update); update();
  }

  // realizácie – filter + rozloženie veľkých dlaždíc
  const gis = $$('.gi'), fb = $$('#filtre button');
  const layout = () => {
    let i = 0;
    gis.forEach(g => { g.classList.remove('big'); if (g.hidden) return; if (i % 7 === 0 && !g.classList.contains('gi--tall')) g.classList.add('big'); i++; });
  };
  fb.forEach(b => b.addEventListener('click', () => {
    fb.forEach(x => x.setAttribute('aria-pressed', x === b));
    const f = b.dataset.f;
    gis.forEach(g => { g.hidden = !(f === 'vse' || g.dataset.k === f); if (!g.hidden) g.classList.add('is-in'); });
    layout();
  }));
  layout();

  // lightbox (len viditeľné)
  const lb = $('#lb'), lbimg = $('#lbimg'), lbcap = $('#lbcap'); let list = [], cur = 0;
  const show = n => {
    cur = (n + list.length) % list.length; const g = list[cur];
    lbimg.src = g.dataset.full; lbimg.alt = $('img', g).alt;
    lbcap.textContent = $('img', g).alt + ' · ' + (cur + 1) + ' / ' + list.length;
  };
  gis.forEach(g => g.addEventListener('click', () => { list = gis.filter(x => !x.hidden); show(list.indexOf(g)); lb.hidden = false; document.body.style.overflow = 'hidden'; }));
  const close = () => { lb.hidden = true; document.body.style.overflow = ''; };
  $('#lbx').addEventListener('click', close);
  lb.addEventListener('click', e => { if (e.target === lb) close(); });
  $('#lbp').addEventListener('click', () => show(cur - 1));
  $('#lbn').addEventListener('click', () => show(cur + 1));
  addEventListener('keydown', e => { if (lb.hidden) return; if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(cur - 1); if (e.key === 'ArrowRight') show(cur + 1); });

  // zloženie modulu – rozloží sa pri zobrazení, vrstva podľa záložky
  const anat = $('#anat');
  if (anat) {
    const tabs = $$('.anat__tabs button'), specs = $$('.spec'), lys = $$('.ly', anat);
    const set = l => {
      tabs.forEach(t => t.setAttribute('aria-selected', t.dataset.l === l));
      specs.forEach(s => s.classList.toggle('is-on', s.dataset.l === l));
      lys.forEach(g => g.classList.toggle('is-on', g.dataset.l === l));
    };
    tabs.forEach(t => t.addEventListener('click', () => { set(t.dataset.l); anat.classList.add('is-open'); }));
    lys.forEach(g => g.addEventListener('click', () => { set(g.dataset.l); anat.classList.add('is-open'); }));
    new IntersectionObserver(([e]) => anat.classList.toggle('is-open', e.isIntersecting), { threshold: .45 }).observe(anat);
    set(tabs[0].dataset.l);
  }

  // dopyt
  $('#dopyt').addEventListener('submit', e => { e.preventDefault(); $('#formok').hidden = false; });
})();
