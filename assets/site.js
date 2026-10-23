(() => {
  const form = document.querySelector('.site-search form');
  if (!form) return;
  const input = form.querySelector('input');
  const output = document.getElementById('search-results');
  const script = [...document.scripts].find(s => s.src.endsWith('/assets/site.js'));
  const base = new URL('../', script.src);
  function search(query) {
    input.value = query;
    output.replaceChildren();
    output.hidden = !query.trim();
    if (output.hidden) return;
    const words = query.toLocaleLowerCase().trim().split(/\s+/);
    const matches = (window.SITE_SEARCH || []).filter(p => words.every(w => (p.title + ' ' + p.text).toLocaleLowerCase().includes(w)));
    const count = document.createElement('p');
    count.textContent = `${matches.length} result${matches.length === 1 ? '' : 's'}`;
    output.append(count);
    for (const page of matches) {
      const link = document.createElement('a');
      link.href = new URL(page.path.replace(/^\//, ''), base);
      link.textContent = page.title;
      output.append(link);
    }
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    const query = input.value.trim();
    search(query);
    const url = new URL(location.href);
    if (query) url.searchParams.set('s', query); else url.searchParams.delete('s');
    history.replaceState(null, '', url);
  });
  const query = new URLSearchParams(location.search).get('s');
  if (query) { search(query); output.scrollIntoView(); }
})();
