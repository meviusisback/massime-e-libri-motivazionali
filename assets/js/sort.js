// Ordinamento delle schede: ogni menu "Ordina" riordina la griglia vicina.
// Criteri: evidenza (ordine originale), data di creazione, anno (nascita o
// pubblicazione), alfabetico. Funziona senza rete, solo DOM locale.
(function () {
  var selects = document.querySelectorAll('select[data-sort]');
  if (!selects.length) return;

  Array.prototype.forEach.call(selects, function (sel) {
    var head = sel.closest ? sel.closest('.grid-head') : null;
    var grid = head ? head.nextElementSibling : null;
    if (!grid || !grid.classList.contains('cards')) return;
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
    cards.forEach(function (c, i) { c.setAttribute('data-pos', i); });

    sel.addEventListener('change', function () {
      var v = sel.value;
      var sorted = cards.slice();
      if (v === 'recent') {
        sorted.sort(function (a, b) {
          var da = a.getAttribute('data-date') || '';
          var db = b.getAttribute('data-date') || '';
          return db < da ? -1 : (db > da ? 1 : 0);
        });
      } else if (v === 'chrono') {
        sorted.sort(function (a, b) {
          var ya = parseInt(a.getAttribute('data-year'), 10);
          var yb = parseInt(b.getAttribute('data-year'), 10);
          if (isNaN(ya) && isNaN(yb)) return 0;
          if (isNaN(ya)) return 1;
          if (isNaN(yb)) return -1;
          return ya - yb;
        });
      } else if (v === 'az') {
        sorted.sort(function (a, b) {
          return (a.getAttribute('data-title') || '').localeCompare(b.getAttribute('data-title') || '', 'it', { sensitivity: 'base' });
        });
      } else {
        sorted.sort(function (a, b) {
          return (+a.getAttribute('data-pos')) - (+b.getAttribute('data-pos'));
        });
      }
      sorted.forEach(function (c) { grid.appendChild(c); });
    });
  });
})();
