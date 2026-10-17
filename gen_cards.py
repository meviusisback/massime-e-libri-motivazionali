#!/usr/bin/env python3
"""Genera gli schemi visuali (SVG) per filosofi e libri: vera infografica
schematica — nodo centrale, 3 nodi collegati, banda con massima breve.
Niente frasi troncate: solo parole chiave e una citazione corta che sta
tutta intera. Solo libreria standard, nessun browser.

Uso: python3 gen_cards.py [slug]  (senza slug: li genera tutti)
"""
import html as H
import os
import re
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
DARK = '#11111b'


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


def lead_of(b):
    m = re.match(r'\*\*(.+?)\*\*\s*:?\s*(.*)', b)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return b.split(':')[0].strip(), b


def all_quotes(bitems):
    out = []
    for b in bitems:
        for m in re.finditer(r'«([^»]+)»', b):
            out.append(m.group(1).strip())
        for m in re.finditer(r'"([^"]{10,})"', b):
            out.append(m.group(1).strip())
    return out


def pick_maxim(quotes):
    """La più corta tra quelle sostanziose (>=30 caratteri), senno la più corta."""
    if not quotes:
        return ''
    pool = [q for q in quotes if len(q) >= 30] or quotes
    return min(pool, key=len)


def node_label(lead):
    """Etichetta nodo: pulita, max 2 righe, mai troncata con puntini."""
    s = lead.strip().rstrip('.')
    if len(s) > 30 and ',' in s:
        s = s.split(',')[0].strip()
    if len(s) <= 26:
        return [s]
    words = s.split()
    l1, l2 = '', ''
    for w in words:
        if not l2 and len((l1 + ' ' + w).strip()) <= 24:
            l1 = (l1 + ' ' + w).strip()
        else:
            l2 = (l2 + ' ' + w).strip()
    return [l1, l2] if l2 else [l1]


def libro_titles(secs):
    out = []
    for key, lines in secs.items():
        if 'CONCETT' in key and 'PORTARE A CASA' in key:
            for b in bullets(lines):
                t, _ = lead_of(b)
                out.append(t)
    if len(out) < 3:
        for key, lines in secs.items():
            m = re.match(r'(\d+)\.\s*(.+)', key)
            if m and not any(w in key for w in ('CITAZIONI', 'ESEMPI', 'APPLICAZIONE', 'PORTARE A CASA', 'LIBRO DEL GIORNO')):
                out.append(m.group(2).strip())
    return out[:3]


def schema_svg(title, sub, center_kw, center_emoji, nodes, maxim):
    ys = [150, 285, 420]
    p = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 660" role="img">',
        '<rect width="1200" height="660" fill="' + BG + '"/>',
        '<circle cx="1080" cy="80" r="180" fill="' + ACCENT + '" opacity="0.06"/>',
        '<circle cx="120" cy="620" r="150" fill="' + ACCENT + '" opacity="0.05"/>',
        '<text x="40" y="62" font-family="system-ui,sans-serif" font-size="38" font-weight="700" fill="' + FG + '">'
        + H.escape(title) + '</text>',
        '<text x="40" y="94" font-family="system-ui,sans-serif" font-size="20" fill="' + MUTED + '">'
        + H.escape(sub) + '</text>',
        '<text x="1160" y="52" font-family="system-ui,sans-serif" font-size="16" letter-spacing="3" fill="' + MUTED
        + '" text-anchor="end">SINTESI VISUALE</text>',
        '<circle cx="320" cy="350" r="122" fill="' + CARD + '" stroke="' + ACCENT + '" stroke-width="3"/>',
        '<text x="320" y="322" font-size="36" text-anchor="middle">' + center_emoji + '</text>',
        '<text x="320" y="372" font-family="system-ui,sans-serif" font-size="31" font-weight="700" fill="' + ACCENT
        + '" text-anchor="middle">' + H.escape(center_kw) + '</text>',
    ]
    for num, lines_kw, y in zip((1, 2, 3), nodes, ys):
        mid = y + 55
        p.append('<line x1="442" y1="350" x2="600" y2="' + str(mid) + '" stroke="' + MUTED
                 + '" stroke-width="2" opacity="0.6"/>')
        p.append('<rect x="600" y="' + str(y) + '" width="540" height="110" rx="20" fill="' + CARD + '"/>')
        p.append('<circle cx="652" cy="' + str(mid) + '" r="24" fill="' + ACCENT + '"/>')
        p.append('<text x="652" y="' + str(mid + 8)
                 + '" font-family="system-ui,sans-serif" font-size="24" font-weight="700" fill="' + DARK
                 + '" text-anchor="middle">' + str(num) + '</text>')
        if len(lines_kw) == 1:
            p.append('<text x="692" y="' + str(mid + 8)
                     + '" font-family="system-ui,sans-serif" font-size="24" font-weight="600" fill="' + FG + '">'
                     + H.escape(lines_kw[0]) + '</text>')
        else:
            p.append('<text x="692" y="' + str(mid - 6)
                     + '" font-family="system-ui,sans-serif" font-size="21" font-weight="600" fill="' + FG + '">'
                     + H.escape(lines_kw[0]) + '</text>')
            p.append('<text x="692" y="' + str(mid + 24)
                     + '" font-family="system-ui,sans-serif" font-size="21" font-weight="600" fill="' + FG + '">'
                     + H.escape(lines_kw[1]) + '</text>')
    mq = '«' + maxim + '»'
    qsize = 22 if len(maxim) <= 85 else 19
    p += [
        '<rect x="40" y="566" width="1100" height="64" rx="16" fill="' + CARD + '" stroke="' + GOLD + '" stroke-width="2"/>',
        '<text x="590" y="607" font-family="system-ui,sans-serif" font-size="' + str(qsize)
        + '" font-style="italic" fill="' + FG + '" text-anchor="middle">' + H.escape(mq) + '</text>',
        '</svg>',
    ]
    return ''.join(p)


def render(slug, kind, meta):
    md = open(os.path.join(CONTENT, kind, slug + '.md'), encoding='utf-8').read()
    secs = sections_of(md)
    if kind == 'filosofi':
        center_kw = meta.get('center', '')
        sub = meta.get('sub', '')
        emoji = '👤'
        tb = bullets(find_secs(secs, 'TEMI'))[:3]
        nodes = [node_label(lead_of(b)[0]) for b in tb]
        mb = bullets(find_secs(secs, 'MASSIME'))
        maxim = pick_maxim(all_quotes(mb))
    else:
        center_kw = meta.get('center', meta.get('topic', ''))
        sub = meta.get('author', '')
        emoji = '📚'
        nodes = [node_label(t) for t in libro_titles(secs)]
        cb = bullets(find_secs(secs, 'CITAZIONI'))
        maxim = pick_maxim(all_quotes(cb))
        if not maxim:
            rb = bullets(find_secs(secs, 'PORTARE A CASA') or find_secs(secs, 'RIASSUNTO'))
            maxim = re.sub(r'\*+', '', rb[0])[:90] if rb else ''
    assert len(nodes) == 3, slug + ' nodi=' + str(len(nodes))
    assert maxim, slug + ' senza massima'
    svg = schema_svg(meta['title'], sub, center_kw, emoji, nodes, maxim)
    open(os.path.join(CARDS, slug + '.svg'), 'w', encoding='utf-8').write(svg)
    print('ok', slug, '| massima:', len(maxim), 'caratteri')


def main():
    import json
    m = json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))
    jobs = [('filosofi', e['slug'], e) for e in m['filosofi']]
    jobs += [('libri', e['slug'], e) for e in m['libri']]
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for kind, slug, meta in jobs:
        if only and slug != only:
            continue
        render(slug, kind, meta)


main()
