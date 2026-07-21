# anki

A really simple Anki-style flashcard app in the browser.

Manage decks and cards, then run study sessions with a minimal spaced-repetition
schedule. Each card can carry an optional hint that stays hidden until you ask for it.

Run it with:

```bash
htools anki
```

Notes:
- it opens a local browser page by default; use `--no-browser` for the URL only
- decks and cards are stored in `anki/data/cards.json` (created on first use)
- each card has a front, a back, and an optional hint (revealed on request)
- study sessions run by time, by number of cards, or free (until the queue is empty)
- grading is two-button: **Again** (resets, shows it again soon) or **Good** (schedules it further out)
- the server is stateless and single-user; it only serves `127.0.0.1`
