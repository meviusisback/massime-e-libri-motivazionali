// Ricerca live della home: filtra le schede mentre digiti.
// Nota sicurezza: ogni stringa dinamica (titoli, query, href) passa da esc(),
// quindi nessun HTML esterno può finire in innerHTML.
(function () {
  var input = document.getElementById('search');
  var box = document.getElementById('search-results');
  if (!input || !box) return;

  function norm(s) {
    return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  var cards = Array.prototype.slice.call(document.querySelectorAll('.cards .card')).map(function (a) {
    var img = a.querySelector('img');
    var h3 = a.querySelector('h3');
    var p = a.querySelector('p');
    var date = a.querySelector('.card-date');
    return {
      href: a.getAttribute('href'),
      img: img ? img.getAttribute('src') : null,
      title: h3 ? h3.textContent : '',
      sub: p ? p.textContent : '',
      date: date ? date.textContent : '',
      kind: a.getAttribute('href').indexOf('filosofi/') === 0 ? '💬' : '📚',
      hay: norm([h3 && h3.textContent, p && p.textContent, date && date.textContent].join(' '))
    };
  });

  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function render(q) {
    q = norm(q.trim());
    if (!q) {
      document.body.classList.remove('searching');
      box.hidden = true;
      box.innerHTML = '';
      return;
    }
    var hits = cards.filter(function (c) { return c.hay.indexOf(q) !== -1; });
    document.body.classList.add('searching');
    box.hidden = false;
    if (!hits.length) {
      box.innerHTML = '<p class="no-results">Nessun risultato per <strong>' + esc(q) + '</strong>.</p>';
      return;
    }
    box.innerHTML = '<p class="results-count">' + hits.length + (hits.length === 1 ? ' risultato' : ' risultati') + '</p>' +
      hits.map(function (c) {
        return '<a class="result-row" href="' + esc(c.href) + '">' +
          (c.img ? '<img src="' + esc(c.img) + '" alt="" loading="lazy">' : '<span class="result-ph">' + c.kind + '</span>') +
          '<span class="result-txt"><strong>' + esc(c.title) + '</strong>' +
          '<span>' + c.kind + ' ' + esc(c.sub) + '</span></span>' +
          '<span class="go">→</span></a>';
      }).join('');
  }

  input.addEventListener('input', function () { render(input.value); });
})();
