#!/usr/bin/env python3
"""Ricostruisce il sito massime-e-libri con layout moderno a sezioni."""
import os, re, json, html as H

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = BASE
CONTENT = os.path.join(BASE, 'content')
MANIFEST = json.load(open(os.path.join(BASE, 'manifest.json'), encoding='utf-8'))
PHILOS = [(e['slug'], e['title'], e['sub'], e['date'], e['img'],
           e['quote'], e['center'], e['chips']) for e in MANIFEST['filosofi']]
BOOKS = [(e['slug'], e['title'], e['author'], e['date'], e['topic'],
          e['center'], e['chips']) for e in MANIFEST['libri']]


SEC_META = {  # chiave nel titolo md -> (icona, etichetta, livello)
 'MASSIMA': ('💬', 'La massima', 'hero'),
 'COMMENTO': ('💬', 'La massima', 'hero'),
 'COME SI LEGGE': ('💬', 'La massima', 'hero'),
 'COSA VUOLE DIRE': ('💬', 'La massima', 'hero'),
 'CHI ERA': ('👤', 'Biografia', 'side'),
 'BIOGRAFIA': ('👤', 'Biografia', 'side'),
 'MOVIMENTI': ('⌛', 'Contesto storico', 'minor'),
 'PERCHÉ CONTA': ('🧭', 'Introduzione', 'body'),
 'VUOI APPROFONDIRE': ('💬', 'Approfondimento in chat', 'minor'),
 'BIO IN BREVE': ('👤', 'Biografia', 'side'),
 'SINTESI': ('📌', 'Sintesi del pensiero', 'key'),
 'CONTESTO': ('⌛', 'Contesto storico', 'minor'),
 'QUIZ': ('🧠', 'Quiz', 'quiz'),
 'SOLUZIONI': ('✅', 'Soluzioni', 'solutions'),
 'RIPASSO': ('🔁', 'Ripasso', 'minor'),
 'INTRODUZIONE': ('🧭', 'Introduzione', 'body'),
 'RIASSUNTO': ('📘', 'Riassunto', 'body'),
 'CONCETTI': ('💡', 'Concetti chiave', 'key'),
 'ESPANSIONE': ('📖', 'Approfondimento', 'body'),
 'APPLICAZIONE': ('🛠️', 'Azioni pratiche', 'key'),
 'AZIONI': ('🛠️', 'Azioni pratiche', 'key'),
 'FRASE': ('💬', 'Frase finale', 'hero'),
 'ESEMPI DI OGGI': ('🌍', 'Esempi di oggi', 'key'),
 'CITAZIONI': ('💬', 'Citazioni da ricordare', 'key'),
 'ESEMPI': ('🌍', 'Esempi di oggi', 'key'),
 'DA PORTARE A CASA': ('💎', 'Da portare a casa', 'hero'),
 'APPROFONDIMENTO IN CHAT': ('💬', 'Approfondimento in chat', 'minor'),
}

def md_inline(t):
    t = H.escape(t)
    for label, cls in [('Come applicarlo', 'do'), ('Come applicarla', 'do'),
                       ('Errore comune', 'err'), ('Definizione', 'def'),
                       ('Collegamento', 'link'), ('Esempio', 'ex')]:
        t = re.sub(r'\*\*' + label + r'\*\*:',
                   f'<span class="lbl lbl-{cls}">' + label + '</span>', t)
        t = re.sub(r'(?<!\*)\*' + label + r':\*',
                   f'<span class="lbl lbl-{cls}">' + label + '</span>', t)
    t = re.sub(r'==(.+?)==', r'<span class="hl">\1</span>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t

def split_paragraphs(lines):
    paras, buf = [], []
    for ln in lines:
        s = ln.strip()
        if s == '':
            if buf: paras.append(' '.join(buf)); buf = []
        elif re.match(r'^[-•]\s|^\d+[.\)]\s|^>\s?', s):
            if buf: paras.append(' '.join(buf)); buf = []
            paras.append(s)
        else:
            buf.append(s)
    if buf: paras.append(' '.join(buf))
    return paras

def render_body(paras):
    """Paragrafi e veri elenchi (niente <br/>)."""
    out, i = [], 0
    while i < len(paras):
        p = paras[i]
        if re.match(r'^[-•]\s', p):
            items = []
            while i < len(paras) and re.match(r'^[-•]\s', paras[i]):
                items.append('<li>' + md_inline(re.sub(r'^[-•]\s', '', paras[i])) + '</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
        elif re.match(r'^\d+\.\s', p):
            items = []
            while i < len(paras) and re.match(r'^\d+\.\s', paras[i]):
                items.append('<li>' + md_inline(re.sub(r'^\d+\.\s', '', paras[i])) + '</li>')
                i += 1
            out.append('<ol>' + ''.join(items) + '</ol>')
        elif re.match(r'^>\s?', p):
            quotes = []
            while i < len(paras) and re.match(r'^>\s?', paras[i]):
                quotes.append(md_inline(re.sub(r'^>\s?', '', paras[i])))
                i += 1
            out.append('<blockquote class="maxim">' + '<br />\n'.join(quotes) + '</blockquote>')
        else:
            out.append('<p>' + md_inline(p) + '</p>')
            i += 1
    return '\n'.join(out)

def render_quiz_from_lines(lines):
    """Quiz dai righe grezze: gestisce tutti i formati (opzioni su righe
    separate, sulla stessa riga, separatori — · o spazi doppi)."""
    out = []
    i, n = 0, len(lines)
    while i < n:
        ln = lines[i].strip()
        qm = re.match(r'^(?:\*\*)?(\d+)[.\)]\s*(?:\*\*)?\s*(.*)', ln)
        if not qm:
            if ln:
                out.append('<p class="quiz-note">' + md_inline(ln) + '</p>')
            i += 1
            continue
        num, rest = qm.group(1), qm.group(2)
        opts = []
        # opzioni eventualmente sulla stessa riga della domanda
        om0 = re.search(r'(?:^|\s)([A-D])[).·]\s', rest)
        if om0 and om0.start() > 0:
            qtext, tail = rest[:om0.start()].rstrip(), rest[om0.start():].strip()
        else:
            qtext, tail = rest, ''
        chunks = [tail] if tail else []
        j = i + 1
        while j < n:
            l2 = lines[j].strip()
            if not l2:
                j += 1
                continue
            if re.match(r'^(?:\*\*)?\d+[.\)]', l2):
                break
            if re.match(r'^[A-D][).·]\s', l2) or re.search(r'\b[A-D][).·]\s', l2):
                chunks.append(l2)
                j += 1
            else:
                break
        for ch in chunks:
            parts = re.split(r'(?:\s+[—–·-]\s+|\s+)(?=[A-D][).·]\s)', ch)
            for p in parts:
                p = p.strip()
                if not p:
                    continue
                mo = re.match(r'^([A-D])[).·]\s*(.*)', p, re.S)
                if mo:
                    opts.append((mo.group(1), mo.group(2)))
        out.append(f'<div class="q"><p class="q-text"><span class="q-num">{num}</span> {md_inline(qtext.strip())}</p>')
        if opts:
            out.append('<ul class="opts">')
            for letter, text in opts:
                out.append(f'<li><span class="opt">{letter}</span> {md_inline(text)}</li>')
            out.append('</ul>')
        out.append('</div>')
        i = j if j > i + 1 else i + 1
    return '\n'.join(out)

KEY_ALIAS = {'COMMENTO': 'MASSIMA', 'COME SI LEGGE': 'MASSIMA',
             'COSA VUOLE DIRE': 'MASSIMA', 'MOVIMENTI': 'CONTESTO',
             'PERCHÉ CONTA': 'INTRODUZIONE', 'VUOI APPROFONDIRE': 'APPROFONDIMENTO IN CHAT',
             'CHI ERA': 'BIOGRAFIA', 'BIO IN BREVE': 'BIOGRAFIA'}

def match_key(title):
    """Chiave canonica di una intestazione. I titoli numerati (sotto-schede
    dei concetti) usano solo frasi strutturali lunghe, mai singole parole
    che possono comparire in un titolo qualsiasi (es. 'vita', 'frase')."""
    up = (title or '').strip().upper()
    plain = re.sub(r'^[^\w]+', '', (title or '').strip()).upper()
    if plain == 'LA VITA':
        return 'BIOGRAFIA'
    if re.match(r'^\d+[.\)]', up):
        if 'ESEMPI DI OGGI' in up:
            return 'ESEMPI DI OGGI'
        if 'APPLICAZIONE PRATICA' in up:
            return 'APPLICAZIONE'
        if 'DA PORTARE A CASA' in up:
            return 'DA PORTARE A CASA'
        if 'APPROFONDIMENTO' in up:
            return 'APPROFONDIMENTO IN CHAT'
        if 'CONCETTI' in up and ('CHIAVE' in up or 'PORTARE' in up or 'CASA' in up):
            return 'CONCETTI'
        for k in ['INTRODUZIONE', 'RIASSUNTO', 'ESPANSIONE', 'QUIZ', 'SOLUZIONI',
                  'RIPASSO', 'MASSIMA', 'SINTESI', 'CONTESTO', 'BIOGRAFIA']:
            if k in up:
                return k
        return 'ALTRO'
    if 'CITAZIONI' in up:
        return 'CITAZIONI'
    _k = next((k for k in SEC_META if k in up), 'ALTRO')
    return KEY_ALIAS.get(_k, _k)

def parse_sections(raw):
    """Divide il markdown in (chiave, titolo_originale, righe).
    Scarta i percorsi dei ritratti e unisce sezioni duplicate."""
    secs, cur_key, cur_title, buf = [], None, None, []
    order = {}
    def flush():
        if cur_key or buf:
            if cur_key and cur_key != 'ALTRO' and cur_key in order:
                secs[order[cur_key]][2].extend(buf)
            else:
                order[cur_key] = len(secs)
                secs.append([cur_key, cur_title, list(buf)])
    for ln in raw.splitlines():
        s = ln.strip()
        if 'ritratto' in s and ('/home/alberto/' in s or s.startswith('/')):
            continue
        if re.match(r'^\(Ritratto[^)]*\)$', s):
            continue
        if re.match(r'^-{3,}\s*$', s):
            continue
        if re.match(r'^\*.*(Wikimedia|Commons|pubblico dominio|Incisione|Ritratto).*\*$', s):
            continue
        m = re.match(r'^(?:\S+\s+)?\*\*(.+?)\*\*\s*$', s)
        h = re.match(r'^#{2,}\s+(.*)', s)
        if m or h:
            flush()
            title = (m.group(1) if m else h.group(1)).strip()
            # riga di sole risposte (es. "1B · 2C · 3A") -> si fonde nelle soluzioni
            if re.match(r'^[1-5][A-E](\s*[·•.,;]\s*[1-5][A-E])+\s*$', title):
                cur_key, cur_title, buf = 'SOLUZIONI', 'Soluzioni', [title]
                continue
            # titolo che è già una citazione -> si fonde nella massima
            if re.match(r'^[«"“]', title):
                cur_key, cur_title, buf = 'MASSIMA', 'La massima', ['> ' + title]
                continue
            up = title.upper()
            cur_key = match_key(title)
            cur_title, buf = title, []
        else:
            buf.append(ln)
    flush()
    return [(k, t, b) for k, t, b in secs if b or k in ('QUIZ', 'SOLUZIONI')]

def section_html(key, title, buf, is_book):
    icon, label, level = SEC_META.get(key, ('📄', title.title(), 'body'))
    if key == 'CITAZIONI':
        items = [re.sub(r'^[-•]\s', '', p).strip()
                 for p in split_paragraphs(buf) if p.strip()]
        body = ''.join('<blockquote class="maxim">' + md_inline(i) + '</blockquote>' for i in items)
        if not body.strip():
            return ''
        return (f'<section class="sec sec-key"><h2><span class="sec-ico">{icon}</span>'
                f'{H.escape(label)}</h2>\n{body}\n</section>')
    if key == 'QUIZ':
        return f'<section class="sec sec-quiz"><h2><span class="sec-ico">{icon}</span>{H.escape(label)}</h2>\n{render_quiz_from_lines(buf)}\n</section>'
    if key == 'SOLUZIONI':
        body = render_body(split_paragraphs(buf))
        return f'<details class="solutions"><summary><span class="sec-ico">{icon}</span>{H.escape(label)} <span class="hint">— tocca per vedere</span></summary>\n{body}\n</details>'
    if key == 'ALTRO':
        body = render_body(split_paragraphs(buf))
        if not body.strip():
            return ''
        t = (title or '').strip()
        ico = '📖' if re.match(r'^\d+[.\)]', t) else '📄'
        h2 = f'<h2><span class="sec-ico">{ico}</span>{H.escape(t)}</h2>\n' if t else ''
        return f'<section class="sec sec-body">{h2}{body}\n</section>'
    lvl_class = {'hero': 'sec-lead', 'key': 'sec-key', 'side': 'sec-side', 'minor': 'sec-minor', 'quiz': 'sec-quiz'}.get(level, 'sec-body')
    return f'<section class="sec {lvl_class}"><h2><span class="sec-ico">{icon}</span>{H.escape(label)}</h2>\n{render_body(split_paragraphs(buf))}\n</section>'

NEW_CSS = r'''
:root{
  --bg:#1e1e2e; --fg:#cdd6f4; --muted:#a6adc8; --card:#313244; --accent:#cba6f7;
  --accent-2:#89b4fa; --border:#45475a; --code:#181825; --gold:#f9e2af; --green:#a6e3a1; --red:#f38ba8;
  --serif:"Fraunces",Georgia,"Times New Roman",serif;
  --sans:"Inter","Segoe UI",system-ui,-apple-system,Roboto,"Helvetica Neue",sans-serif;
}
@media (prefers-color-scheme: light){
  :root{ --bg:#eff1f5; --fg:#4c4f69; --muted:#6c6f85; --card:#ffffff; --accent:#8839ef;
  --accent-2:#1e66f5; --border:#ccd0da; --code:#e6e9ef; --gold:#df8e1d; --green:#40a02b; --red:#d20f39; }
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:var(--sans);background:var(--bg);color:var(--fg);line-height:1.7;font-size:17px}
a{color:var(--accent-2);text-decoration:none}
a:hover{text-decoration:underline}
.site-header{display:flex;align-items:center;justify-content:space-between;gap:1rem;
  padding:.9rem 1.25rem;border-bottom:1px solid var(--border);background:var(--card);
  position:sticky;top:0;z-index:10}
.site-header .home{font-weight:700;color:var(--accent);font-size:1.05rem;white-space:nowrap}
.site-header nav{display:flex;gap:1rem}
.crumb{color:var(--muted);font-size:.85rem;margin:1.5rem 0 0}
.crumb a{color:var(--muted)}
.container{max-width:1080px;margin:0 auto;padding:0 1.25rem 3rem}
.hero{padding:2rem 0 1rem;max-width:760px}
.kicker{display:inline-block;font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:var(--bg);background:var(--accent);border-radius:999px;padding:.3rem .9rem;margin-bottom:.9rem}
.hero h1{font-family:var(--serif);font-size:clamp(2rem,5vw,3rem);line-height:1.15;margin:0 0 .5rem;color:var(--fg)}
.hero .sub{color:var(--muted);font-size:1rem;margin:0 0 1.2rem}
.pullquote{font-family:var(--serif);font-size:clamp(1.25rem,3vw,1.7rem);line-height:1.45;font-style:italic;
  margin:0 0 1.4rem;padding:1.2rem 1.4rem;border-left:5px solid var(--gold);
  background:var(--code);border-radius:0 1rem 1rem 0}
.chips{display:flex;flex-wrap:wrap;gap:.55rem;margin:0 0 1.8rem;padding:0;list-style:none}
.chips li{background:var(--card);border:1px solid var(--border);border-radius:999px;
  padding:.4rem .95rem;font-size:.9rem;color:var(--accent)}
.layout{display:grid;grid-template-columns:1fr;gap:1.2rem}
@media(min-width:960px){ .layout{grid-template-columns:minmax(0,1fr) 300px;align-items:start} }
.sec{background:var(--card);border:1px solid var(--border);border-radius:1rem;
  padding:1.25rem 1.4rem;margin:0 0 1.2rem;overflow:hidden}
.sec h2{font-size:1.05rem;letter-spacing:.02em;margin:0 0 .8rem;padding-bottom:.6rem;
  border-bottom:1px solid var(--border);color:var(--fg);display:flex;align-items:center;gap:.55rem}
.sec-ico{font-size:1.1rem}
.sec p{margin:0 0 .9rem;max-width:70ch;overflow-wrap:break-word}
.sec p:last-child{margin-bottom:0}
.sec strong{color:var(--accent)}
.sec ul,.sec ol{margin:0 0 .9rem;padding-left:1.6rem;max-width:70ch;overflow-wrap:break-word}
.sec li{margin-bottom:.45rem}
.sec li::marker{color:var(--accent);font-weight:700}
.maxim{font-family:var(--serif);font-size:1.12rem;line-height:1.6;font-style:italic;
  margin:0 0 1rem;padding:1rem 1.25rem;border-left:5px solid var(--gold);
  background:var(--code);border-radius:0 .9rem .9rem 0;overflow-wrap:break-word}
.maxim strong{color:var(--gold)}
.lbl{display:inline-block;font-size:.78rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  border:1px solid;border-radius:.45rem;padding:.05rem .55rem;margin-right:.4rem;vertical-align:baseline}
.lbl-def{color:var(--accent-2);border-color:var(--accent-2);background:color-mix(in srgb,var(--accent-2) 12%,transparent)}
.lbl-ex{color:var(--gold);border-color:var(--gold);background:color-mix(in srgb,var(--gold) 12%,transparent)}
.lbl-do{color:var(--green);border-color:var(--green);background:color-mix(in srgb,var(--green) 12%,transparent)}
.lbl-err{color:var(--red);border-color:var(--red);background:color-mix(in srgb,var(--red) 12%,transparent)}
.lbl-link{color:var(--accent);border-color:var(--accent);background:color-mix(in srgb,var(--accent) 12%,transparent)}
.hl{background:color-mix(in srgb,var(--gold) 28%,transparent);border-bottom:2px solid var(--gold);
  padding:0 .15em;border-radius:.2em}
.sec-lead{border-color:var(--gold);background:linear-gradient(180deg,rgba(249,226,175,.07),transparent 60%),var(--card)}
.sec-lead strong{color:var(--gold)}
.sec-key{border-color:var(--accent)}
.sec-key h2{color:var(--accent)}
.sec-minor{opacity:.92}
.sec-minor h2{color:var(--muted);font-size:.95rem}
.sec-body h2{color:var(--accent-2)}
.sec-side h2{color:var(--green)}
.portrait-card{background:var(--card);border:1px solid var(--border);border-radius:1rem;
  overflow:hidden;margin:0 0 1.4rem;max-width:560px}
.portrait-card img{display:block;width:100%;height:auto;object-fit:contain;background:var(--code)}
.portrait-card figcaption{padding:.7rem 1rem;color:var(--muted);font-size:.82rem;font-style:italic}
.facts{background:var(--card);border:1px solid var(--border);border-radius:1rem;
  padding:1.1rem 1.25rem;margin:0 0 1.2rem;font-size:.92rem}
.facts h3{margin:0 0 .6rem;font-size:.85rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.facts ul{margin:0;padding-left:1.2rem}
.facts li{margin-bottom:.35rem}
.sec-quiz{border-color:var(--accent-2)}
.q{padding:.9rem 0;border-top:1px dashed var(--border)}
.q:first-of-type{border-top:none;padding-top:0}
.q-text{font-weight:600;margin:0 0 .6rem}
.q-num{display:inline-flex;align-items:center;justify-content:center;min-width:1.7rem;height:1.7rem;
  border-radius:50%;background:var(--accent-2);color:var(--bg);font-size:.85rem;margin-right:.5rem}
.opts{list-style:none;margin:0;padding:0;display:grid;gap:.5rem}
.opts li{background:var(--code);border:1px solid var(--border);border-radius:.7rem;
  padding:.55rem .8rem;margin:0;overflow-wrap:break-word}
.opt{display:inline-flex;align-items:center;justify-content:center;min-width:1.6rem;height:1.6rem;
  border-radius:.45rem;border:1px solid var(--accent-2);color:var(--accent-2);
  font-weight:700;font-size:.82rem;margin-right:.55rem}
.quiz-note{color:var(--muted);font-size:.92rem}
details.solutions{background:var(--code);border:1px solid var(--green);border-radius:1rem;
  padding:1.1rem 1.3rem;margin:0 0 1.2rem}
details.solutions summary{cursor:pointer;font-weight:700;color:var(--green);font-size:1rem;list-style:none}
details.solutions summary::-webkit-details-marker{display:none}
details.solutions .hint{color:var(--muted);font-weight:400;font-size:.85rem}
details.solutions p,details.solutions ul,details.solutions ol{margin:.7rem 0;max-width:70ch}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.25rem;margin:0 0 2.5rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:1.2rem;overflow:hidden;
  display:flex;flex-direction:column;color:var(--fg);transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease}
.card:hover{transform:translateY(-4px);box-shadow:0 16px 40px rgba(0,0,0,.35);border-color:var(--accent);text-decoration:none}
.card img{width:100%;height:auto;max-height:300px;object-fit:contain;background:var(--code);display:block}
.card-body{padding:1.1rem 1.2rem 1.25rem;display:flex;flex-direction:column;gap:.35rem;flex:1}
.card-date{font-size:.75rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.card-body h3{margin:0;font-family:var(--serif);font-weight:700;font-size:1.35rem;line-height:1.25;color:var(--fg)}
.card-body p{margin:0;color:var(--muted);font-size:.93rem;font-style:italic;font-family:var(--serif)}
.read-more{margin-top:auto;padding-top:.6rem;color:var(--accent);font-weight:600;font-size:.9rem}
.card:hover .read-more{text-decoration:underline}
.section-title{font-family:var(--serif);font-weight:700;font-size:1.8rem;margin:2.4rem 0 1.1rem;display:flex;align-items:center;gap:.6rem}
.count{font-family:var(--sans);font-size:.78rem;font-weight:700;background:var(--code);border:1px solid var(--border);
  color:var(--accent);border-radius:999px;padding:.15rem .7rem}
.hero-cta{display:flex;flex-wrap:wrap;gap:.8rem;margin-top:1.4rem}
.btn{display:inline-block;padding:.65rem 1.4rem;border-radius:999px;font-weight:600;font-size:.95rem;
  border:1px solid var(--border);color:var(--fg)}
.btn:hover{text-decoration:none;border-color:var(--accent)}
.btn-primary{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.btn-primary:hover{filter:brightness(1.08)}
.search-wrap{margin:1.6rem 0 0;max-width:560px;position:relative}
.head-search{margin:0;flex:1;max-width:340px;min-width:140px}
.head-search input{font-size:.92rem;padding:.5rem 1rem .5rem 2.6rem}
.head-search::before{left:.9rem}
.site-header{flex-wrap:wrap;gap:.7rem 1rem}
@media(max-width:640px){.head-search{order:3;flex-basis:100%;max-width:none}}
.search-wrap input{width:100%;font-size:1.05rem;font-family:var(--sans);color:var(--fg);
  background:var(--card);border:1px solid var(--border);border-radius:999px;
  padding:.8rem 1.2rem .8rem 3rem;outline:none}
.search-wrap input:focus{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 25%,transparent)}
.search-wrap::before{content:"🔍";position:absolute;left:1.1rem;top:50%;transform:translateY(-50%);opacity:.7}
body.searching .cards,body.searching .section-title{display:none}
#search-results{margin:1.5rem 0 2.5rem}
#search-results[hidden]{display:none}
.results-count{color:var(--muted);font-size:.9rem;margin:0 0 .8rem}
.no-results{color:var(--muted);background:var(--card);border:1px solid var(--border);
  border-radius:1rem;padding:1.2rem 1.4rem}
.result-row{display:flex;align-items:center;gap:1rem;background:var(--card);
  border:1px solid var(--border);border-radius:1rem;padding:.7rem .9rem;margin-bottom:.6rem;color:var(--fg)}
.result-row:hover{border-color:var(--accent);text-decoration:none}
.result-row img{width:52px;height:52px;object-fit:cover;object-position:top center;
  border-radius:.6rem;flex:none;background:var(--code)}
.result-ph{width:52px;height:52px;flex:none;display:flex;align-items:center;justify-content:center;
  font-size:1.4rem;background:var(--code);border-radius:.6rem}
.result-txt{display:flex;flex-direction:column;gap:.1rem;min-width:0}
.result-txt strong{font-family:var(--serif);font-size:1.05rem}
.result-txt span{color:var(--muted);font-size:.88rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:60ch}
.result-row .go{margin-left:auto;color:var(--accent);font-weight:700;font-size:1.2rem;flex:none}
.page-hero{text-align:left;padding:2.5rem 0 1rem;max-width:760px}
.page-hero h1{font-family:var(--serif);font-size:clamp(2.2rem,6vw,3.4rem);margin:0 0 .6rem}
.page-hero p{color:var(--muted);font-size:1.08rem;margin:0}
footer{padding:2rem 1.25rem;text-align:center;color:var(--muted);border-top:1px solid var(--border);margin-top:1rem}
code{background:var(--code);border:1px solid var(--border);border-radius:.35rem;padding:.05rem .4rem;font-size:.88em}
@media(max-width:640px){ body{font-size:16px} .sec{padding:1rem} }
@media (prefers-reduced-motion: reduce){ *{transition:none} }
'''

SHELL = '''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Biblioteca giornaliera</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,700;1,9..144,500;1,9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
<body>
<header class="site-header">
  <a class="home" href="{prefix}index.html">📚 Biblioteca giornaliera</a>
  <div class="search-wrap head-search"><input id="search" type="search" placeholder="Cerca…" autocomplete="off" aria-label="Cerca nel sito"></div>
  <nav><a href="{prefix}filosofi/">Filosofi</a><a href="{prefix}libri/">Libri</a></nav>
</header>
<script src="{prefix}assets/js/search.js" defer></script>
<main class="container">
{body}
</main>
<footer>Generato da Hermes Agent • Contenuti daily-philosopher &amp; daily-growth-book</footer>
</body>
</html>'''

FILO_RANK = {'MASSIMA': 0, 'SINTESI': 1, 'CONTESTO': 2, 'ESEMPI DI OGGI': 3,
             'ESEMPI': 3, 'QUIZ': 4, 'SOLUZIONI': 5, 'RIPASSO': 6}
LIBRI_RANK = {'INTRODUZIONE': 0, 'RIASSUNTO': 1, 'CONCETTI': 2, 'ESPANSIONE': 3,
              'CITAZIONI': 4, 'ESEMPI DI OGGI': 5, 'ESEMPI': 5, 'APPLICAZIONE': 6, 'AZIONI': 6,
              'FRASE': 7, 'DA PORTARE A CASA': 7, 'APPROFONDIMENTO IN CHAT': 8}

def rank_of(kind, key, title):
    if key in (None, 'ALTRO'):
        if re.match(r'^\d+[.\)]', (title or '').strip()):
            return 3 if kind == 'libri' else 9
        return 9
    table = FILO_RANK if kind == 'filosofi' else LIBRI_RANK
    return table.get(key, 9)

def detail_page(kind, slug, title, sub, date, img, img_cap, quote, chips, raw):
    d = date
    datestr = f'{d[6:8]}/{d[4:6]}/{d[:4]}'
    kicker = '💬 Massima del ' + datestr if kind == 'filosofi' else '📚 Libro · ' + datestr
    img_src = f'../assets/img/{kind}/{img}' if kind == 'filosofi' else f'../assets/img/libri/{slug}.jpg'
    import os as _os
    if kind == 'libri' and not _os.path.exists(os.path.join(ROOT, 'assets/img/libri', slug + '.jpg')):
        fig = ''
    else:
        fig = (f'<figure class="portrait-card"><img src="{img_src}" alt="{H.escape(title)}">'
               f'<figcaption>{H.escape(img_cap)}</figcaption></figure>')
    chip_html = ''.join(f'<li>{H.escape(c)}</li>' for c in chips)
    secs = parse_sections(raw)
    main, aside_extra = [], []
    for idx, (key, t, buf) in enumerate(secs):
        if idx == 0 and key in (None, 'ALTRO'):
            txt = ' '.join(b.strip() for b in buf if b.strip())
            if len(txt) < 300:
                continue
        if not buf and key not in ('QUIZ', 'SOLUZIONI'):
            continue
        h = section_html(key, t or '', buf, kind == 'libri')
        if not h.strip():
            continue
        txt_all = re.sub(r'<[^>]+>', '', h).strip()
        if key in (None, 'ALTRO'):
            if len(txt_all) < 150:
                continue
        if key == 'ESPANSIONE' and len(txt_all) < 150:
            continue
        if key in ('BIOGRAFIA', 'BIO IN BREVE', 'VITA', 'CHI ERA') and kind == 'filosofi':
            aside_extra.append((0, h))
        else:
            main.append((rank_of(kind, key, t), h))
    main.sort(key=lambda x: x[0])
    main = [h for _, h in main]
    aside_extra = [h for _, h in aside_extra]
    crumb = (f'<p class="crumb"><a href="../index.html">Home</a> / '
             f'<a href="./">{"Filosofi" if kind == "filosofi" else "Libri"}</a> / {H.escape(title)}</p>')
    body = f'''{crumb}
<header class="hero">
  {fig}
  <span class="kicker">{kicker}</span>
  <h1>{H.escape(title)}</h1>
  <p class="sub">{H.escape(sub)}</p>
  <blockquote class="pullquote">«{H.escape(quote)}»</blockquote>
  <ul class="chips">{chip_html}</ul>
</header>
<div class="layout">
  <div>
{chr(10).join(main)}
  </div>
  <aside>
    {chr(10).join(aside_extra)}
  </aside>
</div>'''
    return SHELL.format(title=H.escape(title), prefix='../', body=body)

def fmt_date(d):
    return f'{d[6:8]}/{d[4:6]}/{d[:4]}'

def index_cards(items, kind):
    out = []
    for slug, title, sub, date in items:
        import os as _os
        if kind == 'filosofi':
            img = None
            for p in PHILOS:
                if p[0] == slug:
                    img = 'assets/img/filosofi/' + p[4]
        else:
            img = f'assets/img/libri/{slug}.jpg'
            if not _os.path.exists(os.path.join(ROOT, img)):
                img = None
        imgtag = f'<img src="{img}" alt="" loading="lazy">' if img else ''
        out.append(f'<a class="card" href="{kind}/{slug}.html">{imgtag}<div class="card-body">'
                   f'<span class="card-date">{fmt_date(date)}</span><h3>{H.escape(title)}</h3>'
                   f'<p>{H.escape(sub)}</p><span class="read-more">Leggi la scheda →</span></div></a>')
    return '\n'.join(out)

def main():
    os.makedirs(os.path.join(ROOT, 'assets/css'), exist_ok=True)
    open(os.path.join(ROOT, 'assets/css/style.css'), 'w').write(NEW_CSS)
    for slug, name, sub, date, img, quote, center, leaves in PHILOS:
        raw = open(os.path.join(CONTENT, 'filosofi', slug + '.md'), encoding='utf-8').read()
        cap = 'Ritratto — pubblico dominio (Wikimedia Commons)'
        pg = detail_page('filosofi', slug, name, sub, date, img, cap, quote, leaves, raw)
        open(os.path.join(ROOT, 'filosofi', slug + '.html'), 'w', encoding='utf-8').write(pg)
    for slug, title, author, date, topic, center, leaves in BOOKS:
        raw = open(os.path.join(CONTENT, 'libri', slug + '.md'), encoding='utf-8').read()
        pg = detail_page('libri', slug, title, f'{author} · {topic}', date, '', author, title, leaves, raw)
        open(os.path.join(ROOT, 'libri', slug + '.html'), 'w', encoding='utf-8').write(pg)
    fi = [(s, n, q, d) for s, n, m, d, i, q, c, l in PHILOS]
    li = [(s, t, a, d) for s, t, a, d, tp, c, l in BOOKS]
    fidx = SHELL.format(title='Filosofi', prefix='../',
        body='<header class="page-hero"><h1>Filosofi</h1><p>Massime quotidiane: citazione, contesto e quiz.</p></header><div class="cards">'
             + index_cards(fi, 'filosofi') + '</div>')
    open(os.path.join(ROOT, 'filosofi/index.html'), 'w', encoding='utf-8').write(fidx)
    lidx = SHELL.format(title='Libri', prefix='../',
        body='<header class="page-hero"><h1>Libri</h1><p>Riassunti pratici: concetti chiave e azioni.</p></header><div class="cards">'
             + index_cards(li, 'libri') + '</div>')
    open(os.path.join(ROOT, 'libri/index.html'), 'w', encoding='utf-8').write(lidx)
    home = SHELL.format(title='Biblioteca giornaliera', prefix='',
        body=f'''<header class="page-hero"><h1>📚 Biblioteca giornaliera</h1>
<p>Massime filosofiche con quiz e riassunti di libri pratici. Un'idea al giorno, ben evidenziata.</p>
<div class="hero-cta"><a class="btn btn-primary" href="filosofi/">I filosofi</a><a class="btn" href="libri/">I libri</a></div>
<div id="search-results" hidden></div></header>
<h2 class="section-title">💬 Filosofi <span class="count">{len(fi)}</span></h2>
<div class="cards">''' + index_cards(fi, 'filosofi') + f'''</div>
<h2 class="section-title">📚 Libri motivazionali <span class="count">{len(li)}</span></h2>
<div class="cards">''' + index_cards(li, 'libri') + '''</div>''')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(home)
    print('OK pagine:',
          len([s for s in PHILOS]) + len([s for s in BOOKS]) + 3)

main()
