<div align="center">

# Biblioteca giornaliera

**Sito statico su GitHub Pages con una massima filosofica al giorno e riassunti di libri motivazionali: un'idea al giorno, ben evidenziata.**

![Linux](https://img.shields.io/badge/linux-supported-1793d1)

![Esempio di scheda visuale](assets/cards/socrate.svg)

</div>

## Why it exists

Ogni giorno due cron job di Hermes Agent (`massima-filosofica-giornaliera` e `Libro del giorno - crescita personale`) preparano un briefing: una scheda filosofo oppure il riassunto di un libro pratico. Su Telegram arriva solo un messaggio breve con il link — la lettura avviene qui, sul sito, con biografia, sintesi, quiz e concetti chiave in un'unica schermata. Le pagine, gli indici e la home si rigenerano da sole a ogni contenuto.

## Features

- **Sezione filosofi** (`filosofi/`): massima del giorno, biografia, sintesi del pensiero, quiz — i filosofi sono sempre mostrati in ordine cronologico per anno di nascita.
- **Sezione libri** (`libri/`): concetti chiave, azioni pratiche, citazioni da ricordare ed esempi di oggi.
- **Schede visuali SVG** (`assets/cards/`, 41 file): infografica schematica con nodo centrale, 3 nodi collegati e banda con la massima, generate da `gen_cards.py` con la sola libreria standard, senza browser.
- **Ricerca, quiz e ordinamento** sul sito (`assets/js/search.js`, `assets/js/quiz.js`, `assets/js/sort.js`) con stili in `assets/css/style.css`.
- **Ritratti e copertine** in `assets/img/filosofi/` (20 ritratti).
- **Pubblicato su GitHub Pages** dalla branch `main`.

## Install

```bash
git clone https://github.com/meviusisback/massime-e-libri-motivazionali.git
cd massime-e-libri-motivazionali
python3 build_site.py
```

Nessuna dipendenza: solo Python 3 standard e i file del repo.

## Usage

Pubblicare un nuovo contenuto (istruzioni per i cron job):

1. Salva il briefing in `content/filosofi/<slug>.md` o `content/libri/<slug>.md` (`slug` = nome minuscolo, senza accenti, spazi → trattini).
2. Ritratto in `assets/img/filosofi/<slug>.jpg` (o `.png`); copertina libro in `assets/img/libri/<slug>.jpg` (facoltativa).
3. Aggiungi una voce nella lista giusta in `manifest.json` (vedi [Configuration](#configuration)).
4. Nei briefing dei libri usa le intestazioni esatte `**💬 CITAZIONI DA RICORDARE**` e `**🌍 ESEMPI DI OGGI**`, le etichette **Definizione**, **Esempio**, **Come applicarlo**, **Errore comune**, **Collegamento**, e racchiudi i passaggi chiave tra `==` `==`.
5. Lancia `python3 build_site.py` (rigenera tutte le pagine).
6. `git add -A && git commit`, `git pull --rebase`, `git push`.

Non serve altro: le pagine, gli indici e la home si aggiornano da soli.

## Requirements

- Python 3 (sola libreria standard: `gen_cards.py` e `build_site.py` non usano browser né pacchetti esterni).
- `git` per pubblicare (il sito va su GitHub Pages dalla branch `main`).

## Configuration

Tutto vive in [manifest.json](manifest.json): `filosofi` (20 voci) e `libri`.

| Campo | Note |
|---|---|
| `slug` | Nome minuscolo, senza accenti, spazi → trattini; collega briefing, pagina e immagini |
| `title` | Titolo mostrato (es. `Socrate`, `Grit`) |
| `sub` / `author`+`topic` | Filosofi: `Socrate · 470/469–399 a.C.`; libri: autore e tema |
| `date` | Come `YYYYMMDD` (es. `20261031`) |
| `img` | Solo per i filosofi: file in `assets/img/filosofi/` |
| `quote` | La massima / citazione breve |
| `center` | Nodo centrale della scheda visuale (es. `Ignoranza`, `Tenacia`) |
| `chips` | 4 concetti chiave della scheda |
| `year` | Solo filosofi: anno di nascita come intero, **negativo per l'a.C.** (es. `-470` per Socrate); senza `year` il filosofo finisce in fondo |

Regole di ordinamento (vive in `build_site.py`, non nel manifest): i filosofi sono ordinati cronologicamente per `year`, quindi ogni nuovo filosofo va al posto giusto da solo; i libri restano in ordine di pubblicazione e la voce nuova va **in testa** alla lista `libri`.

## How it works

Il briefing markdown in `content/` è la sorgente; `manifest.json` è l'indice; `build_site.py` genera tutte le pagine HTML e `gen_cards.py` le schede SVG.

| Passo | Cosa succede |
|---|---|
| Briefing | Cron Hermes scrive `content/filosofi/<slug>.md` o `content/libri/<slug>.md` |
| Indice | Voce aggiunta in `manifest.json` con `slug`, `date`, `chips` e (filosofi) `year` |
| Build | `python3 build_site.py` rigenera home, indici e schede |
| Pubblicazione | Commit e push su `main` → GitHub Pages |

## Docs

- [manifest.json](manifest.json) — indice di tutti i contenuti
- [build_site.py](build_site.py) — generatore del sito
- [gen_cards.py](gen_cards.py) — generatore delle schede SVG (`python3 gen_cards.py [slug]`)
- [index.html](index.html) — home del sito
- `content/` — briefing sorgente di filosofi e libri
- `filosofi/`, `libri/` — pagine generate

## License

Nessun file LICENSE nel repository.
