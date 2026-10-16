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
 'COMMENTO': ('🔍', 'Commento', 'body'),
 'BIOGRAFIA': ('👤', 'Biografia', 'side'),
 'VITA': ('👤', 'La vita', 'side'),
 'BIO IN BREVE': ('👤', 'Biografia', 'side'),
 'COME SI LEGGE': ('🔍', 'Commento', 'body'),
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
 'ESEMPI': ('🌍', 'Esempi di oggi', 'key'),
 'DA PORTARE A CASA': ('💎', 'Da portare a casa', 'hero'),
 'APPROFONDIMENTO IN CHAT': ('💬', 'Approfondimento in chat', 'minor'),
}

def md_inline(t):
    t = H.escape(t)
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
        m = re.match(r'^(?:\S+\s+)?\*\*(.+?)\*\*\s*$', s)
        h = re.match(r'^#{2,}\s+(.*)', s)
        if m or h:
            flush()
            title = (m.group(1) if m else h.group(1)).strip()
            up = title.upper()
            cur_key = next((k for k in SEC_META if k in up), 'ALTRO')
            cur_title, buf = title, []
        else:
            buf.append(ln)
    flush()
    return [(k, t, b) for k, t, b in secs if b or k in ('QUIZ', 'SOLUZIONI')]

def section_html(key, title, buf, is_book):
    icon, label, level = SEC_META.get(key, ('📄', title.title(), 'body'))
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
  --accent-2:#89b4fa; --border:#45475a; --code:#181825; --gold:#f9e2af; --green:#a6e3a1;
  --serif:Georgia,"Times New Roman",serif;
  --sans:"Segoe UI",system-ui,-apple-system,Roboto,"Helvetica Neue",sans-serif;
}
@media (prefers-color-scheme: light){
  :root{ --bg:#eff1f5; --fg:#4c4f69; --muted:#6c6f85; --card:#ffffff; --accent:#8839ef;
  --accent-2:#1e66f5; --border:#ccd0da; --code:#e6e9ef; --gold:#df8e1d; --green:#40a02b; }
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
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:1rem;margin:0 0 2.5rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:1rem;overflow:hidden;
  display:flex;flex-direction:column;color:var(--fg)}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 32px rgba(0,0,0,.3);text-decoration:none}
.card img{width:100%;height:170px;object-fit:cover;object-position:top center;display:block}
.card-body{padding:1rem 1.1rem}
.card-body h3{margin:0 0 .3rem;font-family:var(--serif);font-size:1.15rem;color:var(--fg)}
.card-body p{margin:0;color:var(--muted);font-size:.9rem;font-style:italic}
.card-tag{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--accent);margin-bottom:.4rem}
.section-title{font-family:var(--serif);font-size:1.7rem;margin:2.2rem 0 1rem}
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
<link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
<body>
<header class="site-header">
  <a class="home" href="{prefix}index.html">📚 Biblioteca giornaliera</a>
  <nav><a href="{prefix}filosofi/">Filosofi</a><a href="{prefix}libri/">Libri</a></nav>
</header>
<main class="container">
{body}
</main>
<footer>Generato da Hermes Agent • Contenuti daily-philosopher &amp; daily-growth-book</footer>
</body>
</html>'''

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
        if key in (None, 'ALTRO'):
            txt = re.sub(r'<[^>]+>', '', h)
            if len(txt.strip()) < 150:
                continue
        if key in ('BIOGRAFIA', 'BIO IN BREVE', 'VITA') and kind == 'filosofi':
            aside_extra.append(h)
        else:
            main.append(h)
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

def index_cards(items, kind):
    out = []
    for slug, title, sub in items:
        img = f'assets/img/{kind}/{slug}.jpg'
        import os as _os
        if kind == 'filosofi':
            # trova ritratto reale
            img = None
            for p in PHILOS:
                if p[0] == slug:
                    img = 'assets/img/filosofi/' + p[4]
        else:
            img = f'assets/img/libri/{slug}.jpg'
            if not _os.path.exists(os.path.join(ROOT, img)):
                img = None
        imgtag = f'<img src="{img}" alt="" loading="lazy">' if img else ''
        tag = '💬 Massima' if kind == 'filosofi' else '📚 Libro'
        out.append(f'<a class="card" href="{kind}/{slug}.html">{imgtag}<div class="card-body">'
                   f'<span class="card-tag">{tag}</span><h3>{H.escape(title)}</h3><p>{H.escape(sub)}</p></div></a>')
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
    fi = [(s, n, q) for s, n, m, d, i, q, c, l in PHILOS]
    li = [(s, t, a) for s, t, a, d, tp, c, l in BOOKS]
    fidx = SHELL.format(title='Filosofi', prefix='../',
        body='<header class="page-hero"><h1>Filosofi</h1><p>Massime quotidiane: citazione, contesto e quiz.</p></header><div class="cards">'
             + index_cards(fi, 'filosofi') + '</div>')
    open(os.path.join(ROOT, 'filosofi/index.html'), 'w', encoding='utf-8').write(fidx)
    lidx = SHELL.format(title='Libri', prefix='../',
        body='<header class="page-hero"><h1>Libri</h1><p>Riassunti pratici: concetti chiave e azioni.</p></header><div class="cards">'
             + index_cards(li, 'libri') + '</div>')
    open(os.path.join(ROOT, 'libri/index.html'), 'w', encoding='utf-8').write(lidx)
    home = SHELL.format(title='Biblioteca giornaliera', prefix='',
        body='''<header class="page-hero"><h1>📚 Biblioteca giornaliera</h1>
<p>Massime filosofiche con quiz e riassunti di libri pratici. Un’idea al giorno, ben evidenziata.</p></header>
<h2 class="section-title">💬 Filosofi</h2>
<div class="cards">''' + index_cards(fi, 'filosofi') + '''</div>
<h2 class="section-title">📚 Libri motivazionali</h2>
<div class="cards">''' + index_cards(li, 'libri') + '</div>')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(home)
    print('OK pagine:',
          len([s for s in PHILOS]) + len([s for s in BOOKS]) + 3)

main()
