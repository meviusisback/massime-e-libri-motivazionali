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
3. Aggiungi una voce nella lista giusta in `manifest.json`
   (campi: `slug`, `title`, `sub`/`author`+`topic`, `date` come `YYYYMMDD`,
   `img` solo per i filosofi, `quote`, `center`, `chips` con 4 concetti).
   Per i **filosofi** aggiungi anche `year`: l'anno di nascita come intero,
   **negativo per il periodo a.C.** (es. `-470` per Socrate, `1632` per Spinoza).
   La posizione nella lista non conta: `build_site.py` ordina i filosofi
   cronologicamente per `year`, quindi ogni nuovo filosofo va al posto giusto
   da solo (senza `year` finirebbe in fondo). I libri restano in ordine di
   pubblicazione: la voce nuova va **in testa** alla lista `libri`.
4. Nei briefing dei libri usa le intestazioni esatte `**💬 CITAZIONI DA RICORDARE**`
   e `**🌍 ESEMPI DI OGGI**`, le etichette **Definizione**, **Esempio**,
   **Come applicarlo**, **Errore comune**, **Collegamento** (il sito le colora
   da solo) e racchiudi i passaggi chiave tra `==` `==` per evidenziarli.
5. Lancia `python3 build_site.py` (rigenera tutte le pagine).
6. `git add -A && git commit`, `git pull --rebase`, `git push`.

Non serve altro: le pagine, gli indici e la home si aggiornano da soli.
