// Mobile nav
const toggle = document.querySelector('.nav-toggle');
const nav = document.getElementById('site-nav');
toggle?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  toggle.setAttribute('aria-expanded', String(open));
});
nav?.addEventListener('click', (e) => {
  if (e.target.closest('a')) {
    nav.classList.remove('open');
    toggle?.setAttribute('aria-expanded', 'false');
  }
});

// Season tabs (with arrow-key support)
const tabs = [...document.querySelectorAll('.seasons [role="tab"]')];
function select(tab) {
  tabs.forEach((t) => {
    const on = t === tab;
    t.setAttribute('aria-selected', String(on));
    t.tabIndex = on ? 0 : -1;
    document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
  });
}
tabs.forEach((tab, i) => {
  tab.addEventListener('click', () => select(tab));
  tab.addEventListener('keydown', (e) => {
    const dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
    if (!dir) return;
    const next = tabs[(i + dir + tabs.length) % tabs.length];
    select(next);
    next.focus();
  });
});

// Open the current season by default
const m = new Date().getMonth(); // 0 = Jan
const current = m >= 5 && m <= 7 ? 'summer' : m >= 8 && m <= 9 ? 'fall' : m >= 3 && m <= 4 ? 'spring' : 'winter';
const currentTab = document.getElementById(`t-${current}`);
if (currentTab) select(currentTab);

// Footer year
const y = document.getElementById('year');
if (y) y.textContent = new Date().getFullYear();
