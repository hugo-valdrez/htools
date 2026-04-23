import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from abstract.conditions import ConditionsManager
from utils.readers.reader_factory import ReaderFactory

DISHES_PATH = Path(__file__).parent / "configs" / "dishes.yaml"
CONDITIONS_PATH = Path(__file__).parent / "configs" / "conditions.yaml"


def solve_meal_plan(current_plan, remaining_dishes):
    if not conditions_manager.can_still_satisfy(
        meal_selection=current_plan, remaining_dishes=remaining_dishes
    ):
        return None

    if len(current_plan) == conditions_manager.meal_plan_size:
        if conditions_manager.check_conditions(meal_selection=current_plan):
            return current_plan
        return None

    indices = list(range(len(remaining_dishes)))
    random.shuffle(indices)

    for idx in indices:
        selection = remaining_dishes[idx]
        new_remaining = remaining_dishes[:idx] + remaining_dishes[idx + 1 :]

        result = solve_meal_plan(current_plan + [selection], new_remaining)
        if result is not None:
            return result

    return None


if __name__ == "__main__":
    dishes_reader = ReaderFactory.create_reader(file_path=DISHES_PATH)
    available_dishes = dishes_reader.read()["dishes"]

    conditions_reader = ReaderFactory.create_reader(file_path=CONDITIONS_PATH)
    config = conditions_reader.read()

    profile_name = (
        sys.argv[1] if len(sys.argv) > 1 else config.get("default_profile", "default")
    )
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        raise ValueError(f"Unknown profile: {profile_name}")

    conditions_manager = ConditionsManager.from_profile(profiles[profile_name])
    meal_plan = solve_meal_plan([], available_dishes)
    print(meal_plan)
