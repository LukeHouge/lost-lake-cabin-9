(() => {
  const root = document.documentElement;
  const motion = root.classList.contains('motion');
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];

  // Run fn once when el scrolls into view (immediately if IO is unavailable).
  const onceVisible = (el, fn, margin = '0px 0px -12% 0px') => {
    if (!el) return;
    if (!('IntersectionObserver' in window)) return fn();
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { io.disconnect(); fn(); }
    }, { rootMargin: margin });
    io.observe(el);
  };

  // ----- header: solid after scrolling past the top -----
  const header = $('.site-header');
  const onScrollHeader = () => header.classList.toggle('scrolled', window.scrollY > 40);
  onScrollHeader();
  window.addEventListener('scroll', onScrollHeader, { passive: true });

  // ----- mobile nav -----
  const toggle = $('.nav-toggle');
  const nav = $('#site-nav');
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  nav.addEventListener('click', (e) => {
    if (e.target.closest('a')) { nav.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); }
  });

  // ----- 4. season theme switcher: crossfade + falling leaves for fall -----
  const leafBox = $('.leaves');
  const dropLeaves = () => {
    if (!motion || !leafBox) return;
    leafBox.replaceChildren();
    const colors = ['#d9822b', '#c2541b', '#e9b23b', '#a8401a', '#f0a73a'];
    for (let i = 0; i < 12; i++) {
      const leaf = document.createElement('span');
      leaf.className = 'leaf';
      const st = leaf.style;
      st.setProperty('--x', `${Math.random() * 100}%`);
      st.setProperty('--s', `${10 + Math.random() * 12}px`);
      st.setProperty('--c', colors[i % colors.length]);
      st.setProperty('--dur', `${6 + Math.random() * 4}s`);
      st.setProperty('--delay', `${Math.random() * 2.5}s`);
      st.setProperty('--dx', `${(Math.random() - .3) * 260}px`);
      st.setProperty('--rot', `${(Math.random() - .5) * 900}deg`);
      leafBox.appendChild(leaf);
    }
    setTimeout(() => leafBox.replaceChildren(), 13000);
  };

  const flurryBox = $('.flurry');
  const dropSnow = () => {
    if (!motion || !flurryBox) return;
    flurryBox.replaceChildren();
    for (let i = 0; i < 70; i++) {
      const f = document.createElement('span');
      f.className = 'flake';
      const size = 3 + Math.random() * 8;
      const st = f.style;
      st.setProperty('--x', `${Math.random() * 100}%`);
      st.setProperty('--s', `${size}px`);
      st.setProperty('--b', `${size > 8 ? 1.2 : 0}px`);           // bigger = closer = softer
      st.setProperty('--o', (0.55 + Math.random() * 0.45).toFixed(2));
      st.setProperty('--dur', `${7 + Math.random() * 6}s`);
      st.setProperty('--delay', `${Math.random() * 4}s`);
      st.setProperty('--dx', `${(Math.random() - .5) * 120}px`);
      flurryBox.appendChild(f);
    }
    setTimeout(() => flurryBox.replaceChildren(), 17000);
  };
  const setFavicon = (season) => { const fav = $('#favicon'); if (fav) fav.href = `assets/img/logo-${season}.svg`; };

  const btns = $$('[data-season-btn]');
  const mark = (choice) => btns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.seasonBtn === choice)));
  let saved = null;
  try { saved = localStorage.getItem('c9-season'); } catch (e) {}
  mark(new URLSearchParams(location.search).get('season') || saved || 'auto');
  btns.forEach((b) => b.addEventListener('click', () => {
    const choice = b.dataset.seasonBtn;
    const season = choice === 'auto' ? root.dataset.autoSeason : choice;
    try { choice === 'auto' ? localStorage.removeItem('c9-season') : localStorage.setItem('c9-season', choice); } catch (e) {}
    const url = new URL(location.href);
    choice === 'auto' ? url.searchParams.delete('season') : url.searchParams.set('season', choice);
    history.replaceState(null, '', url);
    mark(choice);
    if (season === root.dataset.season) return;
    const apply = () => { root.dataset.season = season; setFavicon(season); updateDay(); };
    if (motion && document.startViewTransition) document.startViewTransition(apply);
    else apply();
    if (season === 'fall') setTimeout(dropLeaves, 400);
    if (season === 'winter') setTimeout(dropSnow, 400);
  }));
  if (root.dataset.season === 'fall') setTimeout(dropLeaves, root.classList.contains('intro') ? 1800 : 300);
  if (root.dataset.season === 'winter') setTimeout(dropSnow, root.classList.contains('intro') ? 1800 : 300);

  // ----- accent illustrations: on/off toggle + logbook wallpaper -----
  const accBtn = $('[data-accents]');
  const syncAcc = () => accBtn && accBtn.setAttribute('aria-pressed', String(!root.classList.contains('no-accents')));
  syncAcc();
  accBtn?.addEventListener('click', () => {
    const off = root.classList.toggle('no-accents');
    try { localStorage.setItem('c9-accents', off ? 'off' : 'on'); } catch (e) {}
    const url = new URL(location.href);
    off ? url.searchParams.set('accents', 'off') : url.searchParams.delete('accents');
    history.replaceState(null, '', url);
    syncAcc();
  });
  const pattern = $('.logbook .pattern');
  if (pattern) {
    const keys = ['loon', 'sunset', 'oars', 'golf', 'skis', 'fish', 'fire', 'snow', 'pine', 'canoe', 'leaf', 'mug', 'rod', 'wave', 'moon'];
    let seed = 11;
    const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
    let out = '<svg xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" viewBox="0 0 1600 900">';
    for (let y = 18, row = 0; y < 900; y += 74, row++) {
      for (let x = (row % 2) * 48 + 14; x < 1600; x += 96) {
        const k = keys[Math.floor(rnd() * keys.length)];
        const r = ((rnd() - .5) * 34).toFixed(1);
        out += `<use href="#i-${k}" x="${x}" y="${y}" width="30" height="30" transform="rotate(${r} ${x + 15} ${y + 15})" fill="none" stroke="rgba(255,255,255,.075)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>`;
      }
    }
    pattern.innerHTML = out + '</svg>';
  }

  // ----- lightbox -----
  const dlg = $('.lightbox');
  const dlgImg = $('img', dlg);
  let items = [];
  let idx = 0;
  const visibleItems = () => $$('[data-lightbox]').filter((el) => el.offsetParent !== null);
  const show = (i) => {
    idx = (i + items.length) % items.length;
    const el = items[idx];
    dlgImg.src = el.dataset.lightbox;
    dlgImg.alt = $('img', el)?.alt || '';
  };
  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-lightbox]');
    if (!el) return;
    items = visibleItems();
    show(Math.max(0, items.indexOf(el)));
    dlg.showModal();
  });
  $('.lb-close', dlg).addEventListener('click', () => dlg.close());
  $('.lb-prev', dlg).addEventListener('click', () => show(idx - 1));
  $('.lb-next', dlg).addEventListener('click', () => show(idx + 1));
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') show(idx - 1);
    if (e.key === 'ArrowRight') show(idx + 1);
  });

  // ----- 9. floor explorer (tabs) -----
  const tabs = $$('.house [role="tab"]');
  const selectFloor = (tab, focus) => {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      const panel = $('#' + t.getAttribute('aria-controls'));
      panel.hidden = !on;
      if (on && motion) { panel.classList.remove('enter'); void panel.offsetWidth; panel.classList.add('enter'); }
    });
    if (focus) tab.focus();
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => selectFloor(tab));
    tab.addEventListener('keydown', (e) => {
      const dir = ['ArrowDown', 'ArrowRight'].includes(e.key) ? 1 : ['ArrowUp', 'ArrowLeft'].includes(e.key) ? -1 : 0;
      if (!dir) return;
      e.preventDefault();
      selectFloor(tabs[(i + dir + tabs.length) % tabs.length], true);
    });
  });

  // ----- 2. map: draw on scroll + legend <-> marker highlighting -----
  const mapFrame = $('.map-frame');
  if (mapFrame) {
    if (motion) {
      onceVisible(mapFrame, () => {
        mapFrame.classList.add('drawn');
        setTimeout(() => mapFrame.classList.add('settled'), 4200);
      }, '0px 0px -25% 0px');
    } else {
      mapFrame.classList.add('drawn', 'settled');
    }
    const legend = $$('.map-legend li[data-poi]');
    const pois = $$('.map-poi[data-poi]', mapFrame);
    const hot = (n) => {
      legend.forEach((li) => li.classList.toggle('hot', li.dataset.poi === n));
      pois.forEach((g) => g.classList.toggle('hot', g.dataset.poi === n));
    };
    const cool = () => hot(null);
    [...legend, ...pois].forEach((el) => {
      el.addEventListener('mouseenter', () => hot(el.dataset.poi));
      el.addEventListener('mouseleave', cool);
      el.addEventListener('focus', () => hot(el.dataset.poi));
      el.addEventListener('blur', cool);
      el.addEventListener('click', () => hot(el.dataset.poi));
    });
  }

  // ----- map zoom: whole lake <-> north end (tweens the SVG viewBox) -----
  const mapSvg = $('.lake-map');
  const zoomBtns = $$('.map-zoom [data-view]');
  let zoomAnim = 0;
  const setView = (target) => {
    const from = mapSvg.getAttribute('viewBox').split(/\s+/).map(Number);
    const to = target.split(/\s+/).map(Number);
    cancelAnimationFrame(zoomAnim);
    if (!motion) { mapSvg.setAttribute('viewBox', target); return; }
    const t0 = performance.now(), dur = 900;
    const step = (now) => {
      const k = Math.min(1, (now - t0) / dur);
      const e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
      mapSvg.setAttribute('viewBox', from.map((f, i) => (f + (to[i] - f) * e).toFixed(1)).join(' '));
      if (k < 1) zoomAnim = requestAnimationFrame(step);
      else mapSvg.setAttribute('viewBox', target);
    };
    zoomAnim = requestAnimationFrame(step);
    setTimeout(() => mapSvg.setAttribute('viewBox', target), dur + 100);
  };
  zoomBtns.forEach((b) => b.addEventListener('click', () => {
    zoomBtns.forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    mapFrame.classList.toggle('zoomed', b !== zoomBtns[0]);
    setView(b.dataset.view);
  }));
  // tapping "Downtown Nisswa" in the legend zooms to the north end
  $('.map-legend li[data-poi="9"]')?.addEventListener('click', () => zoomBtns[1]?.click());

  // ----- 3. day-to-dusk timeline driven by scroll -----
  const day = $('#day');
  let ticking = false;
  function updateDay() {
    ticking = false;
    if (!motion || !day) return;
    const r = day.getBoundingClientRect();
    const vh = window.innerHeight;
    // 0 when the section's top reaches 75% of the viewport, 1 when its bottom reaches 45%
    const p = Math.min(1, Math.max(0, (vh * .75 - r.top) / (r.height + vh * .3)));
    day.style.setProperty('--p', p.toFixed(3));
    day.classList.toggle('night', p > .78);
    const step = Math.min(4, Math.floor(p * 5));
    $$('.timeline li[data-step]', day).forEach((li) => {
      const s = +li.dataset.step;
      li.classList.toggle('active', s === step);
      li.classList.toggle('past', s < step);
    });
  }
  if (day && motion) {
    window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(updateDay); } }, { passive: true });
    window.addEventListener('resize', updateDay);
    updateDay();
  }

  // ----- 7. fact counters -----
  const counters = $$('[data-count]');
  if (motion && counters.length) {
    counters.forEach((c) => { c.textContent = '0'; });
    onceVisible($('.facts'), () => {
      const start = performance.now();
      const dur = 1100;
      const tick = (now) => {
        const t = Math.min(1, (now - start) / dur);
        const eased = 1 - Math.pow(1 - t, 3);
        counters.forEach((c) => { c.textContent = String(Math.round(+c.dataset.count * eased)); });
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      // guarantee the final numbers even if frames are throttled (background tab, etc.)
      setTimeout(() => counters.forEach((c) => { c.textContent = c.dataset.count; }), dur + 150);
    });
  }

  // ----- reveal on scroll -----
  if (motion && 'IntersectionObserver' in window) {
    const targets = $$('.section-head, .stay-card, .lake-card, .perk, .season-card, .explore-grid article, .collage, .notes, .explorer, .gallery');
    targets.forEach((t) => t.classList.add('reveal'));
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    targets.forEach((t) => io.observe(t));
  }

  const y = $('#year');
  if (y) y.textContent = new Date().getFullYear();
})();
