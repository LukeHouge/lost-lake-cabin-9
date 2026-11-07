(() => {
  const root = document.documentElement;

  // ----- header: solid after scrolling past the top -----
  const header = document.querySelector('.site-header');
  const onScroll = () => header.classList.toggle('scrolled', window.scrollY > 40);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // ----- mobile nav -----
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('site-nav');
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  nav.addEventListener('click', (e) => {
    if (e.target.closest('a')) { nav.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); }
  });

  // ----- season theme switcher -----
  const btns = document.querySelectorAll('[data-season-btn]');
  const mark = (choice) => btns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.seasonBtn === choice)));
  let saved = null;
  try { saved = localStorage.getItem('c9-season'); } catch (e) {}
  const q = new URLSearchParams(location.search).get('season');
  mark(q || saved || 'auto');
  btns.forEach((b) => b.addEventListener('click', () => {
    const choice = b.dataset.seasonBtn;
    const season = choice === 'auto' ? root.dataset.autoSeason : choice;
    try { choice === 'auto' ? localStorage.removeItem('c9-season') : localStorage.setItem('c9-season', choice); } catch (e) {}
    const url = new URL(location.href);
    choice === 'auto' ? url.searchParams.delete('season') : url.searchParams.set('season', choice);
    history.replaceState(null, '', url);
    root.dataset.season = season;
    mark(choice);
  }));

  // ----- lightbox -----
  const dlg = document.querySelector('.lightbox');
  const dlgImg = dlg.querySelector('img');
  const items = [...document.querySelectorAll('[data-lightbox]')];
  let idx = 0;
  const show = (i) => {
    idx = (i + items.length) % items.length;
    const el = items[idx];
    dlgImg.src = el.dataset.lightbox;
    dlgImg.alt = el.querySelector('img')?.alt || '';
  };
  items.forEach((el, i) => el.addEventListener('click', () => { show(i); dlg.showModal(); }));
  dlg.querySelector('.lb-close').addEventListener('click', () => dlg.close());
  dlg.querySelector('.lb-prev').addEventListener('click', () => show(idx - 1));
  dlg.querySelector('.lb-next').addEventListener('click', () => show(idx + 1));
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') show(idx - 1);
    if (e.key === 'ArrowRight') show(idx + 1);
  });

  // ----- reveal on scroll -----
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const targets = document.querySelectorAll('.section-head, .level, .stay-card, .lake-card, .perk, .season-card, .explore-grid article, .collage, .timeline li, .map-frame, .notes');
    targets.forEach((t) => t.classList.add('reveal'));
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    targets.forEach((t) => io.observe(t));
  }

  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
