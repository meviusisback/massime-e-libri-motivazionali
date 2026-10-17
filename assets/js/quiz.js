// Quiz interattivo: seleziona, verifica subito, copia il codice per la chat.
// Nota sicurezza: gli unici innerHTML usano sol.html (contenuto statico del sito,
// generato dal builder) e stringhe già filtrate da esc(); nessuna fonte esterna.
(function () {
  var sec = document.querySelector('.sec-quiz');
  if (!sec) return;

  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // Lettera corretta per domanda, letta dalle soluzioni della pagina.
  var solMap = {};
  Array.prototype.forEach.call(document.querySelectorAll('details.solutions li'), function (li) {
    var m = li.textContent.match(/^\s*(\d+)[.\)]\s*([A-D])\b/);
    if (m && !solMap[m[1]]) solMap[m[1]] = { letter: m[2], html: li.innerHTML };
  });

  var questions = Array.prototype.slice.call(sec.querySelectorAll('.q'));
  if (!questions.length) return;
  var checkBtn = sec.querySelector('.quiz-check');
  var copyBtn = sec.querySelector('.quiz-copy');
  var scoreEl = sec.querySelector('.quiz-score');
  var copyMsg = sec.querySelector('.quiz-copy-msg');
  var title = sec.getAttribute('data-quiz') || 'Quiz';

  function selectedLetter(q) {
    var r = q.querySelector('input[type="radio"]:checked');
    return r ? r.value : null;
  }

  function check() {
    var tot = 0, ok = 0;
    questions.forEach(function (q) {
      var numEl = q.querySelector('.q-num');
      var num = numEl ? numEl.textContent.trim() : String(tot + 1);
      tot++;
      var sel = selectedLetter(q);
      var sol = solMap[num];
      q.classList.remove('q-ok', 'q-ko');
      Array.prototype.forEach.call(q.querySelectorAll('.opts li'), function (li) {
        li.classList.remove('mark-correct', 'mark-wrong');
      });
      var old = q.querySelector('.q-explain');
      if (old) old.parentNode.removeChild(old);
      if (sol) {
        Array.prototype.forEach.call(q.querySelectorAll('.opts li'), function (li) {
          var r = li.querySelector('input[type="radio"]');
          if (r && r.value === sol.letter) li.classList.add('mark-correct');
          if (r && sel && r.checked && sel !== sol.letter) li.classList.add('mark-wrong');
        });
      }
      var good = !!(sel && sol && sel === sol.letter);
      if (good) ok++;
      q.classList.add(good ? 'q-ok' : 'q-ko');
      if (sol) {
        var p = document.createElement('p');
        p.className = 'q-explain';
        p.innerHTML = '<strong>' + (good ? 'Esatto.' : 'Sbagliato.') + '</strong> ' + sol.html;
        q.appendChild(p);
      }
    });
    if (scoreEl) scoreEl.textContent = 'Punteggio: ' + ok + '/' + tot + (ok === tot ? ' — perfetto!' : ' — leggi le spiegazioni qui sopra.');
    if (copyMsg) copyMsg.textContent = '';
  }

  function code() {
    var parts = questions.map(function (q, i) {
      var sel = selectedLetter(q);
      return (i + 1) + (sel || '-');
    });
    return 'Quiz ' + title + ': ' + parts.join(' ');
  }

  function copy() {
    var s = code();
    function done(sent) {
      if (copyMsg) copyMsg.textContent = sent
        ? 'Copiato: ' + s + ' — incollalo in chat e ti correggo con punteggio e ripasso.'
        : 'Copia manuale: ' + s;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(s).then(function () { done(true); }, function () { done(false); });
    } else done(false);
  }

  if (checkBtn) checkBtn.addEventListener('click', check);
  if (copyBtn) copyBtn.addEventListener('click', copy);
})();
