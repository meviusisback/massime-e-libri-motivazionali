import json

path = "/home/alberto/.hermes/profiles/philosopher/workspace/daily-growth-book/used.json"
with open(path, encoding="utf-8") as f:
    used = json.load(f)

entry = {"titolo": "Pre-Suasion (Pre-Suasion: A Revolutionary Way to Influence and Persuade)", "autore": "Robert B. Cialdini"}
if not any(e.get("titolo") == entry["titolo"] for e in used):
    used.append(entry)

with open(path, "w", encoding="utf-8") as f:
    json.dump(used, f, ensure_ascii=False, indent=2)
    f.write("\n")

print("used.json aggiornato, totale:", len(used))
