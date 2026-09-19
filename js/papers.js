/* Publications page: All / Peer-Reviewed / Preprints tabs.
   Papers carry data-type="peer-reviewed" or data-type="preprint" in
   papers/index.html; year headings hide themselves when a filter empties them. */
(() => {
  const bar = document.querySelector('.pub-filter');
  if (!bar) return;

  const tabs    = Array.from(bar.querySelectorAll('.pub-filter-btn'));
  const papers  = Array.from(document.querySelectorAll('.papers-page .paper'));
  const groups  = Array.from(document.querySelectorAll('.papers-page .year-group'));
  const empty   = document.querySelector('.pub-empty');
  const VALID   = tabs.map(t => t.dataset.filter);

  // Tab counts
  tabs.forEach(tab => {
    const f = tab.dataset.filter;
    const n = f === 'all' ? papers.length : papers.filter(p => p.dataset.type === f).length;
    const slot = tab.querySelector('.pub-count');
    if (slot) slot.textContent = n;
  });

  function apply(filter, { push = true } = {}) {
    if (!VALID.includes(filter)) filter = 'all';

    let shown = 0;
    papers.forEach(paper => {
      const match = filter === 'all' || paper.dataset.type === filter;
      paper.hidden = !match;
      if (match) shown++;
    });

    // A year with nothing left to show loses its heading too
    groups.forEach(group => {
      const any = Array.from(group.querySelectorAll('.paper')).some(p => !p.hidden);
      group.hidden = !any;
    });

    tabs.forEach(tab => {
      const on = tab.dataset.filter === filter;
      tab.classList.toggle('is-active', on);
      tab.setAttribute('aria-selected', String(on));
      tab.tabIndex = on ? 0 : -1;
    });

    if (empty) empty.hidden = shown > 0;

    if (push) {
      const url = new URL(window.location);
      if (filter === 'all') url.searchParams.delete('show');
      else url.searchParams.set('show', filter);
      history.replaceState(null, '', url);
    }
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => apply(tab.dataset.filter));

    // Left/right arrows move between tabs, as a tablist should
    tab.addEventListener('keydown', e => {
      const step = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!step) return;
      e.preventDefault();
      const next = tabs[(tabs.indexOf(tab) + step + tabs.length) % tabs.length];
      apply(next.dataset.filter);
      next.focus();
    });
  });

  apply(new URLSearchParams(window.location.search).get('show') || 'all', { push: false });
})();
