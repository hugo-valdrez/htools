import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import yaml


def assign_runtime_ids(dishes):
    slug_counts = {}
    normalized_dishes = []

    for dish in dishes:
        dish_copy = dict(dish)
        base_slug = slugify(dish_copy["name"])
        occurrence = slug_counts.get(base_slug, 0) + 1
        slug_counts[base_slug] = occurrence

        meal_id = base_slug if occurrence == 1 else f"{base_slug}-{occurrence}"
        dish_copy["id"] = meal_id
        normalized_dishes.append(dish_copy)

    return normalized_dishes


def load_history(history_path):
    if not history_path.exists():
        return {"history": {}}

    with history_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    history = data.get("history")
    if not isinstance(history, dict):
        return {"history": {}}

    return {"history": history}


def get_history_sets(history_data, profile_name):
    profile_history = history_data.get("history", {}).get(profile_name, [])
    latest_ids = (
        set(profile_history[0].get("meal_ids", [])) if profile_history else set()
    )
    previous_ids = (
        set(profile_history[1].get("meal_ids", []))
        if len(profile_history) > 1
        else set()
    )
    return latest_ids, previous_ids - latest_ids


def save_history_entry(history_path, history_data, profile_name, meal_plan):
    history = history_data.setdefault("history", {})
    profile_history = history.setdefault(profile_name, [])
    profile_history.insert(
        0,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "meal_ids": [dish["id"] for dish in meal_plan],
        },
    )
    history[profile_name] = profile_history[:2]

    with history_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(history_data, file, sort_keys=False, allow_unicode=True)


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    lower_value = ascii_value.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lower_value).strip("-")
    return slug or "meal"
