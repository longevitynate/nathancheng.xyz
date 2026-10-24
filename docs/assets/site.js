(() => {
  'use strict';
  const script = [...document.scripts].find(s => new URL(s.src, location.href).pathname.endsWith('/assets/site.js'));
  if (!script) return;
  const base = new URL('../', script.src);
  const initialQuery = new URLSearchParams(location.search).get('s') || '';
  const forms = [...document.querySelectorAll('.site-search form')];

  function showResults(form, query) {
    const section = form.closest('.site-search');
    const input = form.querySelector('input');
    const output = section.querySelector('.search-results');
    input.value = query;
    output.replaceChildren();
    output.hidden = !query.trim();
    if (output.hidden) return;
    const words = query.toLocaleLowerCase().trim().split(/\s+/);
    const matches = (window.SITE_SEARCH || []).filter(page =>
      words.every(word => (page.title + ' ' + page.text).toLocaleLowerCase().includes(word)));
    const count = document.createElement('p');
    count.textContent = matches.length + ' result' + (matches.length === 1 ? '' : 's');
    output.append(count);
    for (const page of matches) {
      const link = document.createElement('a');
      link.href = new URL(page.path.replace(/^\//, ''), base).href;
      link.textContent = page.title;
      output.append(link);
    }
  }

  for (const form of forms) {
    form.addEventListener('submit', event => {
      event.preventDefault();
      const query = form.querySelector('input').value.trim();
      showResults(form, query);
      const url = new URL(location.href);
      if (query) url.searchParams.set('s', query); else url.searchParams.delete('s');
      history.replaceState(null, '', url);
    });
  }

  const searchButton = document.querySelector('.header-search-button');
  const searchPanel = document.getElementById('header-search');
  searchButton?.addEventListener('click', () => {
    searchPanel.hidden = !searchPanel.hidden;
    searchButton.setAttribute('aria-expanded', String(!searchPanel.hidden));
    if (!searchPanel.hidden) searchPanel.querySelector('input').focus();
  });
  const menuButton = document.querySelector('.menu-button');
  const menu = document.getElementById('main-nav');
  menuButton?.addEventListener('click', () => {
    const open = menu.classList.toggle('is-open');
    menuButton.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    for (const details of document.querySelectorAll('details[open]')) details.open = false;
    if (!searchPanel.hidden) {
      searchPanel.hidden = true;
      searchButton.setAttribute('aria-expanded', 'false');
      searchButton.focus();
    }
    menu.classList.remove('is-open');
    menuButton.setAttribute('aria-expanded', 'false');
  });
  if (initialQuery) {
    const form = document.querySelector('.hero .site-search form') || searchPanel.querySelector('form');
    if (searchPanel.contains(form)) {
      searchPanel.hidden = false;
      searchButton.setAttribute('aria-expanded', 'true');
    }
    showResults(form, initialQuery);
  }
})();
