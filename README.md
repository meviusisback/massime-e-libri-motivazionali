# Biblioteca giornaliera

Sito GitHub Pages con:
- sezione `filosofi/`: massime quotidiane dei filosofi (biografia, sintesi, quiz)
- sezione `libri/`: riassunti di libri motivazionali (concetti chiave, azioni pratiche)

Contenuti generati da Hermes Agent (cron `massima-filosofica-giornaliera` e `Libro del giorno - crescita personale`).
Su Telegram arriva solo un messaggio breve con il link: la lettura avviene sul sito.

Pubblicato su GitHub Pages dalla branch `main`.

## Come pubblicare un nuovo contenuto (istruzioni per i cron job)

1. Salva il briefing in `content/filosofi/<slug>.md` o `content/libri/<slug>.md`
   (`slug` = nome minuscolo, senza accenti, spazi → trattini).
2. Ritratto in `assets/img/filosofi/<slug>.jpg` (o `.png`);
   copertina libro in `assets/img/libri/<slug>.jpg` (facoltativa).
3. Aggiungi una voce in testa alla lista giusta in `manifest.json`
   (campi: `slug`, `title`, `sub`/`author`+`topic`, `date` come `YYYYMMDD`,
   `img` solo per i filosofi, `quote`, `center`, `chips` con 4 concetti).
4. Lancia `python3 build_site.py` (rigenera tutte le pagine).
5. `git add -A && git commit`, `git pull --rebase`, `git push`.

Non serve altro: le pagine, gli indici e la home si aggiornano da soli.
