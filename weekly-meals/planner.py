import random

from abstract.conditions import ConditionsManager


def solve_meal_plan(current_plan, remaining_dishes):
    if conditions_manager.check_conditions(meal_selection=current_plan):
        return current_plan

    if len(current_plan) >= 7 or not remaining_dishes:
        return None

    indices = list(range(len(remaining_dishes)))
    random.shuffle(indices)

    for idx in indices:
        selection = remaining_dishes[idx]
        new_remaining = remaining_dishes[:idx] + remaining_dishes[idx+1:]

        result = solve_meal_plan(current_plan + [selection], new_remaining)
        if result is not None:
            return result

    return None


if __name__ == "__main__":
    conditions_manager = ConditionsManager()
    solve_meal_plan()