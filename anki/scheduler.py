from __future__ import annotations

from datetime import date, timedelta

RATINGS = ("again", "good")
MAX_INTERVAL = 365


def today() -> str:
    return date.today().isoformat()


def new_fields() -> dict:
    return {"interval": 0, "due": today()}


def review(card: dict, rating: str) -> None:
    if rating == "again":
        card["interval"] = 0
    elif card["interval"] == 0:
        card["interval"] = 1
    else:
        card["interval"] = min(card["interval"] * 2, MAX_INTERVAL)
    card["due"] = (date.today() + timedelta(days=card["interval"])).isoformat()


def is_due(card: dict, on: str | None = None) -> bool:
    return card["due"] <= (on or today())
