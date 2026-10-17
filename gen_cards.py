#!/usr/bin/env python3
"""Genera le schede visuali (PNG 16:9) per filosofi e libri.

Uso: python3 gen_cards.py [slug]  (senza slug: li genera tutti)
Strumenti: solo libreria standard + chromium di sistema (nessun pip).
"""
import html as H
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, 'content')
CARDS = os.path.join(ROOT, 'assets', 'cards')
os.makedirs(CARDS, exist_ok=True)

BG = '#1e1e2e'
CARD = '#313244'
FG = '#cdd6f4'
MUTED = '#a6adc8'
ACCENT = '#cba6f7'
GOLD = '#f9e2af'
GREEN = '#a6e3a1'
BLUE = '#89b4fa'


def trunc(s, n):
    s = ' '.join(s.split())
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(' ', 1)[0]
    return (cut or s[:n]) + '…'


def sections_of(md):
    secs = {}
    cur = None
    hdr = re.compile(r'^\*\*(.+)\*\*\s*$')
    for ln in md.splitlines():
        m = hdr.match(ln.strip())
        if m and '**:' not in ln:
            cur = m.group(1).strip().upper()
            secs.setdefault(cur, [])
        elif cur is not None:
            secs[cur].append(ln)
    return secs


def find_secs(secs, *wants):
    for key, lines in secs.items():
        if any(w in key for w in wants):
            return [l for l in lines if l.strip()]
    return []


def bullets(lines):
    out = []
    for l in lines:
        s = l.strip()
        if s.startswith('- '):
            out.append(s[2:].strip())
            continue
        m = re.match(r'^\d+\.\s+(.*)', s)
        if m:
            out.append(m.group(1).strip())
    return out


def clean_desc(d):
    """Toglie l'etichetta iniziale (**Definizione:** ...) e restituisce il testo."""
    d = d.strip()
    m = re.match(r'^\*\*(.+?)\*\*\s*:?\s*(.*)$', d)
    if m and len(m.group(1).split()) <= 3:
        return m.group(2).strip()
    return d


def libro_concetti(secs):
    """(titolo, descrizione) x N: prima dalla sezione riepilogo, poi dagli header numerati."""
    out = []
    for key, lines in secs.items():
        if 'CONCETT' in key and 'PORTARE A CASA' in key:
            for b in bullets(lines):
                t, d = lead_of(b)
                out.append((t, d))
    if len(out) < 3:
        for key, lines in secs.items():
            m = re.match(r'(\d+)\.\s*(.+)', key)
            if m and not any(w in key for w in ('CITAZIONI', 'ESEMPI', 'APPLICAZIONE', 'PORTARE A CASA', 'LIBRO DEL GIORNO')):
                first = next(iter(bullets(lines)), '')
                out.append((m.group(2).strip(), clean_desc(first)))
    return out[:4]


def libro_azioni(secs):
    """(titolo_colonna, voci): Applicazione, senno Da portare a casa, senno Esempi."""
    for wants, title in (('APPLICAZIONE', 'Azioni'),
                         ('PORTARE A CASA', 'Da portare a casa'),
                         ('ESEMPI', 'Esempi')):
        for key, lines in secs.items():
            if wants in key:
                items = [re.sub(r'\*+', '', b) for b in bullets(lines)[:4]]
                if items:
                    return title, items
    return 'Azioni', []


def lead_of(b):
    m = re.match(r'\*\*(.+?)\*\*\s*:?\s*(.*)', b)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return b.split(':')[0].strip(), b


def quotes_of(bitems):
    out = []
    for b in bitems:
        m = re.search(r'«([^»]+)»', b)
        if m:
            out.append(m.group(1).strip())
    return out


def inline_md(t):
    t = H.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'==(.+?)==', r'<mark>\1</mark>', t)
    return t


CARD_CSS = (
    '*{margin:0;padding:0;box-sizing:border-box}'
    'body{width:1280px;height:720px;background:' + BG + ';color:' + FG + ';'
    'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;'
    'display:flex;flex-direction:column;padding:28px 32px;overflow:hidden}'
    '.head{display:flex;align-items:center;gap:20px;margin-bottom:20px}'
    '.head img{width:96px;height:96px;object-fit:cover;border-radius:50%;'
    'border:3px solid ' + ACCENT + ';flex:none;background:' + CARD + '}'
    '.head h1{font-size:38px;line-height:1.1}'
    '.head p{color:' + MUTED + ';font-size:19px;margin-top:4px}'
    '.grid{flex:1;display:grid;grid-template-columns:1.15fr 1fr 1fr;gap:18px;min-height:0}'
    '.box{background:' + CARD + ';border-radius:16px;padding:18px 20px;overflow:hidden;'
    'display:flex;flex-direction:column;justify-content:center}'
    '.box h2{font-size:20px;margin-bottom:12px}'
    '.box h2 .dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px}'
    '.box ul{list-style:none}'
    '.box li{font-size:18px;line-height:1.42;margin-bottom:10px}'
    '.box li strong{color:' + GOLD + '}'
    '.box .q{font-size:18px;line-height:1.45;border-left:4px solid ' + GOLD + ';'
    'padding-left:12px;margin-bottom:12px;font-style:italic}'
    '.foot{margin-top:16px;color:' + MUTED + ';font-size:15px;display:flex;'
    'justify-content:space-between}'
    'mark{background:rgba(249,226,175,.25);color:' + GOLD + ';padding:0 4px;border-radius:4px}'
)


def card_html(title, sub, img_src, cols, foot):
    boxes = []
    for color, h, body in cols:
        boxes.append(
            '<div class="box"><h2><span class="dot" style="background:' + color + '"></span>'
            + H.escape(h) + '</h2>' + body + '</div>')
    img = '<img src="' + img_src + '" alt="">' if img_src else ''
    return ('<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><style>'
            + CARD_CSS + '</style></head><body>'
            '<div class="head">' + img + '<div><h1>' + H.escape(title) + '</h1><p>'
            + H.escape(sub) + '</p></div></div>'
            '<div class="grid">' + ''.join(boxes) + '</div>'
            '<div class="foot"><span>' + H.escape(foot) + '</span>'
            '<span>massime-e-libri-motivazionali</span></div>'
            '<script>try{document.querySelectorAll(".box").forEach(function(b)'
            '{if(b.scrollHeight>b.clientHeight+1)b.setAttribute("data-overflow","1")})}'
            'catch(e){}</script>'
            '</body></html>')


def filo_card(slug, meta, md):
    secs = sections_of(md)
    sint = ' '.join(find_secs(secs, 'SINTESI'))[:400]
    sint = trunc(re.sub(r'\*+', '', sint), 380)
    temi = bullets(find_secs(secs, 'TEMI'))[:3]
    temi_li = ''.join('<li><strong>' + H.escape(lead_of(b)[0])
                      + '</strong> — ' + inline_md(trunc(lead_of(b)[1], 90)) + '</li>'
                      for b in temi)
    mass_items = bullets(find_secs(secs, 'MASSIME'))[:2]
    mass_html = ''
    for b in mass_items:
        mq = re.search(r'«[^»]+»', b)
        q = mq.group(0) if mq else b
        rest = trunc(re.sub(r'\*+', '', b.replace(q, '', 1)).lstrip(' —–-.:;'), 120)
        mass_html += '<div class="q">' + H.escape(trunc(q, 160)) + '</div>'
        if rest:
            mass_html += '<ul><li>' + inline_md(rest) + '</li></ul>'
    opere = bullets(find_secs(secs, 'OPERE'))[:3]
    opere_li = ''.join('<li><strong>' + H.escape(trunc(lead_of(b)[0], 60)) + '</strong> — '
                       + inline_md(trunc(lead_of(b)[1], 100)) + '</li>'
                       for b in opere)
    img = 'file://' + os.path.join(ROOT, 'assets', 'img', 'filosofi', meta.get('img', ''))
    if not meta.get('img') or not os.path.exists(os.path.join(ROOT, 'assets', 'img', 'filosofi', meta.get('img', ''))):
        img = ''
    sub = meta.get('dates', meta.get('sub', ''))
    cols = [(ACCENT, 'Sintesi', '<ul><li>' + inline_md(sint) + '</li></ul>' + '<ul>' + temi_li + '</ul>'),
            (GOLD, 'Massime', mass_html or '<ul><li>—</li></ul>'),
            (GREEN, 'Opere', '<ul>' + opere_li + '</ul>')]
    return card_html(meta['title'], sub, img, cols, 'Sintesi visuale · ' + meta['title'])


def libro_card(slug, meta, md):
    secs = sections_of(md)
    conc = libro_concetti(secs)
    conc_li = ''.join('<li><strong>' + H.escape(t)
                      + '</strong>' + (' — ' + inline_md(trunc(d, 100)) if d else '') + '</li>'
                      for t, d in conc)
    cits = quotes_of(bullets(find_secs(secs, 'CITAZIONI')))[:3]
    frase = trunc(' '.join(find_secs(secs, 'PORTARE A CASA'))[:200].replace('*', ''), 140)
    if not frase.strip():
        rb = bullets(find_secs(secs, 'RIASSUNTO'))
        if rb:
            frase = trunc(re.sub(r'\*+', '', rb[0]), 140)
    cit_html = ''.join('<div class="q">' + H.escape(trunc(q, 180)) + '</div>' for q in cits)
    if frase:
        cit_html += '<ul><li>' + inline_md(frase) + '</li></ul>'
    az_title, az = libro_azioni(secs)
    az_li = ''.join('<li>' + inline_md(trunc(b, 110)) + '</li>' for b in az)
    img = 'file://' + os.path.join(ROOT, 'assets', 'img', 'libri', slug + '.jpg')
    if not os.path.exists(os.path.join(ROOT, 'assets', 'img', 'libri', slug + '.jpg')):
        img = ''
    cols = [(BLUE, 'Concetti chiave', '<ul>' + conc_li + '</ul>'),
            (GOLD, 'Da ricordare', cit_html or '<ul><li>—</li></ul>'),
            (GREEN, az_title, '<ul>' + az_li + '</ul>')]
    return card_html(meta['title'], meta.get('author', ''), img, cols,
                     'Sintesi visuale · ' + meta['title'])


def render(slug, kind, meta):
    md = open(os.path.join(CONTENT, kind, slug + '.md'), encoding='utf-8').read()
    html = filo_card(slug, meta, md) if kind == 'filosofi' else libro_card(slug, meta, md)
    hp = os.path.join(CARDS, slug + '.html')
    pp = os.path.join(CARDS, slug + '.png')
    open(hp, 'w', encoding='utf-8').write(html)
    r = subprocess.run(['chromium', '--headless', '--no-sandbox', '--disable-gpu',
                        '--hide-scrollbars', '--force-device-scale-factor=2',
                        '--window-size=1280,720', '--virtual-time-budget=3000',
                        '--screenshot=' + pp, hp],
                       capture_output=True, text=True, timeout=120)
    if not os.path.exists(pp) or os.path.getsize(pp) < 10000:
        print('FALLITA', slug, (r.stderr or '')[-200:])
        return False
    print('ok', slug, os.path.getsize(pp) // 1024, 'KB')
    return True


def main():
    import json
    m = json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))
    jobs = []
    for e in m['filosofi']:
        jobs.append(('filosofi', e['slug'], e))
    for e in m['libri']:
        jobs.append(('libri', e['slug'], e))
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ok, no = 0, 0
    for kind, slug, meta in jobs:
        if only and slug != only:
            continue
        if render(slug, kind, meta):
            ok += 1
        else:
            no += 1
    print('fatte:', ok, 'fallite:', no)


main()
