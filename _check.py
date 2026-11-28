import json
m = json.load(open('/home/alberto/repo/massime-e-libri-motivazionali/manifest.json'))
for e in m['filosofi']:
    if 'heidegger' in e.get('slug', '') or 'foucault' in e.get('slug', '') or 'popper' in e.get('slug', ''):
        print(e)
