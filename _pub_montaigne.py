import json, shutil, os

REPO = "/home/alberto/repo/massime-e-libri-motivazionali"
SRC = "/home/alberto/.hermes/profiles/philosopher/workspace/daily-philosopher/2026-11-06-ritratto.jpg"
DST = os.path.join(REPO, "assets/img/filosofi/michel-de-montaigne.jpg")

shutil.copyfile(SRC, DST)
print("copied portrait, bytes:", os.path.getsize(DST))

mp = os.path.join(REPO, "manifest.json")
with open(mp, "r", encoding="utf-8") as f:
    data = json.load(f)

slugs = [e.get("slug") for e in data.get("filosofi", [])]
if "michel-de-montaigne" in slugs:
    print("entry already present, skipping insert")
else:
    entry = {
        "slug": "michel-de-montaigne",
        "title": "Michel de Montaigne",
        "sub": "Michel de Montaigne · 1533–1592",
        "date": "20261106",
        "img": "michel-de-montaigne.jpg",
        "quote": "La più grande cosa del mondo è saper appartenere a se stessi",
        "center": "Sé stessi",
        "chips": ["Scetticismo", "Solitudine", "Io", "Tolleranza"],
        "year": 1533,
    }
    data["filosofi"].append(entry)
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("manifest entry added")
