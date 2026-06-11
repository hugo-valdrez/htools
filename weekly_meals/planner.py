import random
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from weekly_meals.abstract.conditions import ConditionsManager
from weekly_meals.history import (
    assign_runtime_ids,
    get_history_sets,
    load_history,
    save_history_entry,
)
from utils.readers.reader_factory import ReaderFactory

DISHES_PATH = Path(__file__).parent / "configs" / "dishes.yaml"
CONDITIONS_PATH = Path(__file__).parent / "configs" / "conditions.yaml"
HISTORY_PATH = Path(__file__).parent / "configs" / "history.yaml"
HISTORY_PENALTY_WEIGHT = 0.25


def weighted_indices(dishes):
    weighted_candidates = [
        (idx, dish.get("selection_weight", 1.0)) for idx, dish in enumerate(dishes)
    ]
    ordered_indices = []

    while weighted_candidates:
        total_weight = sum(weight for _, weight in weighted_candidates)
        if total_weight <= 0:
            random.shuffle(weighted_candidates)
            ordered_indices.extend(idx for idx, _ in weighted_candidates)
            break

        threshold = random.uniform(0, total_weight)
        running_weight = 0.0

        for position, (idx, weight) in enumerate(weighted_candidates):
            running_weight += weight
            if threshold <= running_weight:
                ordered_indices.append(idx)
                weighted_candidates.pop(position)
                break

    return ordered_indices


def parse_swap_input(raw, plan_size):
    tokens = [token for token in raw.replace(",", " ").split() if token]
    if not tokens:
        return None

    slots = set()
    for token in tokens:
        if not token.isdigit():
            return None
        position = int(token)
        if position < 1 or position > plan_size:
            return None
        slots.add(position - 1)

    if not slots or len(slots) >= plan_size:
        return None

    return sorted(slots)


def swap_slots(
    meal_plan,
    slots_to_swap,
    all_dishes,
    blocked_ids,
    deprioritized_ids,
    conditions_manager,
):
    kept_indices = [i for i in range(len(meal_plan)) if i not in set(slots_to_swap)]
    kept_meals = [meal_plan[i] for i in kept_indices]
    kept_ids = {dish["id"] for dish in kept_meals}

    pool = prepare_dishes_for_history(
        all_dishes,
        blocked_ids=blocked_ids,
        deprioritized_ids=deprioritized_ids,
    )
    pool = [dish for dish in pool if dish["id"] not in kept_ids]

    result = solve_meal_plan(list(kept_meals), pool, conditions_manager)
    if result is None:
        return None

    replacements = result[len(kept_meals) :]
    new_plan = list(meal_plan)
    for slot, replacement in zip(sorted(slots_to_swap), replacements):
        new_plan[slot] = replacement

    return new_plan


def prompt_swap_or_save(
    meal_plan,
    profile_name,
    all_dishes,
    blocked_ids,
    deprioritized_ids,
    conditions_manager,
):
    current_plan = meal_plan

    while True:
        try:
            choice = input("[s]wap meals, sa[v]e, [q]uit (no save): ").strip().lower()
        except EOFError:
            return current_plan, False

        if choice in {"v", "save"}:
            return current_plan, True
        if choice in {"q", "quit"}:
            return current_plan, False
        if choice not in {"s", "swap"}:
            continue

        try:
            raw = input(f"Slots to regenerate (1-{len(current_plan)}, e.g. 3 or 3,5): ")
        except EOFError:
            return current_plan, False

        slots = parse_swap_input(raw, len(current_plan))
        if slots is None:
            print(
                "Invalid selection. Enter slot numbers within range and fewer "
                "than the full plan."
            )
            continue

        new_plan = swap_slots(
            current_plan,
            slots,
            all_dishes=all_dishes,
            blocked_ids=blocked_ids,
            deprioritized_ids=deprioritized_ids,
            conditions_manager=conditions_manager,
        )

        human_slots = ", ".join(str(slot + 1) for slot in slots)
        if new_plan is None:
            print(f"No valid swap found for slot(s) {human_slots} — original kept.")
            continue

        current_plan = new_plan
        print()
        print_meal_plan(current_plan, profile_name)


def prepare_dishes_for_history(dishes, blocked_ids, deprioritized_ids):
    prepared_dishes = []

    for dish in dishes:
        if dish["id"] in blocked_ids:
            continue

        dish_copy = dict(dish)
        dish_copy["selection_weight"] = (
            HISTORY_PENALTY_WEIGHT if dish_copy["id"] in deprioritized_ids else 1.0
        )
        prepared_dishes.append(dish_copy)

    return prepared_dishes


def print_meal_plan(meal_plan, profile_name):
    print("Weekly Meal Plan")
    print(f"Profile: {profile_name}")
    print(f"Meals: {len(meal_plan)}")
    print()

    for index, dish in enumerate(meal_plan, start=1):
        attrs = dish.get("attrs", {})
        legume = attrs.get("legume") or "no"

        print(f"  {index}. {dish['name']}")
        print(
            "     "
            f"protein: {attrs.get('protein', 'n/a')}"
            f" | carb: {attrs.get('carb', 'n/a')}"
            f" | legume: {legume}"
        )
        print()

    print_meal_summary(meal_plan)


def print_meal_summary(meal_plan):
    protein_counts = count_attr_values(meal_plan, "protein")
    carb_counts = count_attr_values(meal_plan, "carb")
    legume_dishes = sum(1 for dish in meal_plan if dish.get("attrs", {}).get("legume"))

    print("Summary")
    print(f"- protein: {format_counts(protein_counts)}")
    print(f"- carb: {format_counts(carb_counts)}")
    print(f"- legume dishes: {legume_dishes}")


def count_attr_values(meal_plan, attr_name):
    counts = {}

    for dish in meal_plan:
        value = dish.get("attrs", {}).get(attr_name, "n/a")
        counts[value] = counts.get(value, 0) + 1

    return counts


def format_counts(counts):
    return " | ".join(f"{value} x{count}" for value, count in sorted(counts.items()))


def solve_meal_plan(current_plan, remaining_dishes, conditions_manager):
    if not conditions_manager.can_still_satisfy(
        meal_selection=current_plan, remaining_dishes=remaining_dishes
    ):
        return None

    if len(current_plan) == conditions_manager.meal_plan_size:
        if conditions_manager.check_conditions(meal_selection=current_plan):
            return current_plan
        return None

    indices = weighted_indices(remaining_dishes)

    for idx in indices:
        selection = remaining_dishes[idx]
        new_remaining = remaining_dishes[:idx] + remaining_dishes[idx + 1 :]

        result = solve_meal_plan(
            current_plan + [selection], new_remaining, conditions_manager
        )
        if result is not None:
            return result

    return None


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    dishes_reader = ReaderFactory.create_reader(file_path=DISHES_PATH)
    all_dishes = assign_runtime_ids(dishes_reader.read()["dishes"])

    conditions_reader = ReaderFactory.create_reader(file_path=CONDITIONS_PATH)
    config = conditions_reader.read()

    profile_name = (
        argv[0] if len(argv) > 0 else config.get("default_profile", "default")
    )
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        raise ValueError(f"Unknown profile: {profile_name}")

    conditions_manager = ConditionsManager.from_profile(profiles[profile_name])
    history_data = load_history(HISTORY_PATH)
    blocked_ids, deprioritized_ids = get_history_sets(history_data, profile_name)
    available_dishes = prepare_dishes_for_history(
        all_dishes,
        blocked_ids=blocked_ids,
        deprioritized_ids=deprioritized_ids,
    )

    meal_plan = solve_meal_plan([], available_dishes, conditions_manager)
    if meal_plan is None:
        print("No valid meal plan found.")
        return

    print_meal_plan(meal_plan, profile_name)
    final_plan, should_save = prompt_swap_or_save(
        meal_plan,
        profile_name,
        all_dishes=all_dishes,
        blocked_ids=blocked_ids,
        deprioritized_ids=deprioritized_ids,
        conditions_manager=conditions_manager,
    )
    if should_save:
        save_history_entry(HISTORY_PATH, history_data, profile_name, final_plan)


if __name__ == "__main__":
    main()
