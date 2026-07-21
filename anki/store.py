from __future__ import annotations

import json
import random
import threading
from pathlib import Path
from uuid import uuid4

from anki import scheduler

DATA_PATH = Path(__file__).with_name("data") / "cards.json"
_LOCK = threading.Lock()


def _new_id() -> str:
    return uuid4().hex[:8]


def _load() -> dict:
    if not DATA_PATH.exists():
        return {"decks": []}
    with DATA_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not isinstance(data.get("decks"), list):
        return {"decks": []}
    return data


def _save(data: dict) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def _find_deck(data: dict, deck_id: str) -> dict | None:
    return next((deck for deck in data["decks"] if deck["id"] == deck_id), None)


def list_decks() -> list[dict]:
    with _LOCK:
        data = _load()
        return [
            {
                "id": deck["id"],
                "name": deck["name"],
                "count": len(deck["cards"]),
                "due": sum(1 for card in deck["cards"] if scheduler.is_due(card)),
            }
            for deck in data["decks"]
        ]


def add_deck(name: str) -> dict:
    with _LOCK:
        data = _load()
        deck = {"id": _new_id(), "name": name, "cards": []}
        data["decks"].append(deck)
        _save(data)
        return deck


def delete_deck(deck_id: str) -> None:
    with _LOCK:
        data = _load()
        data["decks"] = [deck for deck in data["decks"] if deck["id"] != deck_id]
        _save(data)


def list_cards(deck_id: str) -> list[dict]:
    with _LOCK:
        data = _load()
        deck = _find_deck(data, deck_id)
        return list(deck["cards"]) if deck else []


def add_card(deck_id: str, front: str, back: str, hint: str) -> dict | None:
    with _LOCK:
        data = _load()
        deck = _find_deck(data, deck_id)
        if deck is None:
            return None
        card = {"id": _new_id(), "front": front, "back": back, "hint": hint}
        card.update(scheduler.new_fields())
        deck["cards"].append(card)
        _save(data)
        return card


def delete_card(deck_id: str, card_id: str) -> None:
    with _LOCK:
        data = _load()
        deck = _find_deck(data, deck_id)
        if deck is None:
            return
        deck["cards"] = [card for card in deck["cards"] if card["id"] != card_id]
        _save(data)


def study(deck_id: str, include_all: bool = False) -> list[dict]:
    with _LOCK:
        data = _load()
        deck = _find_deck(data, deck_id)
        if deck is None:
            return []
        cards = [c for c in deck["cards"] if include_all or scheduler.is_due(c)]
        random.shuffle(cards)
        return cards


def apply_review(deck_id: str, card_id: str, rating: str) -> bool:
    with _LOCK:
        data = _load()
        deck = _find_deck(data, deck_id)
        if deck is None:
            return False
        card = next((c for c in deck["cards"] if c["id"] == card_id), None)
        if card is None:
            return False
        scheduler.review(card, rating)
        _save(data)
        return True
