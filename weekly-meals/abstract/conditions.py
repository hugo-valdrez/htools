from abstract.base_condition import BaseCondition


class ConditionsManager:
    def __init__(self, **kwargs):
        self.conditions = [
            mandatory_MealPlanSize(meal_plan_size=kwargs.get("meal_plan_size")),
            mandatory_TofuDishes(tofu_dishes_size=kwargs.get("tofu_dishes_size")),
            mandatory_FishDishes(fish_dishes_size=kwargs.get("fish_dishes_size")),
            mandatory_LegumeDishes(legume_dishes_size=kwargs.get("legume_dishes_size")),
            minimum_PastaDishes(pasta_dishes_size=kwargs.get("pasta_dishes_size")),
            minimum_RiceDishes(rice_dishes_size=kwargs.get("rice_dishes_size")),
            minimum_PotatoDishes(potato_dishes_size=kwargs.get("potato_dishes_size")),
            maximum_LegumeRepeated(maximum_repeated_legume=kwargs.get("maximum_repeated_legume"))
        ]

    def check_conditions(self, meal_selection):
        for condition in self.conditions:
            if not condition.satisfies_condition(meal_selection=meal_selection):
                return False
        return True


class mandatory_MealPlanSize(BaseCondition):
    def __init__(self, meal_plan_size: int = 7):
        self.meal_plan_size = meal_plan_size

    def satisfies_condition(self, meal_selection):
        return len(meal_selection) == self.meal_plan_size


class minimum_PastaDishes(BaseCondition):
    def __init__(self, pasta_dishes_size: int = 1):
        self.pasta_dishes_size = pasta_dishes_size

    def satisfies_condition(self, meal_selection):
        return (
            sum(1 for dish in meal_selection if dish["carb"] == "Pasta")
            >= self.pasta_dishes_size
        )


class minimum_RiceDishes(BaseCondition):
    def __init__(self, rice_dishes_size: int = 1):
        self.rice_dishes_size = rice_dishes_size

    def satisfies_condition(self, meal_selection):
        return (
            sum(1 for dish in meal_selection if dish["carb"] == "Rice")
            >= self.rice_dishes_size
        )


class minimum_PotatoDishes(BaseCondition):
    def __init__(self, potato_dishes_size: int = 1):
        self.potato_dishes_size = potato_dishes_size

    def satisfies_condition(self, meal_selection):
        return (
            sum(1 for dish in meal_selection if dish["carb"] == "Potato")
            >= self.potato_dishes_size
        )


class mandatory_TofuDishes(BaseCondition):
    def __init__(self, tofu_dishes_size: int = 2):
        self.tofu_dishes_size = tofu_dishes_size

    def satisfies_condition(self, meal_selection):
        return (
            sum(1 for dish in meal_selection if dish["protein"] == "Tofu")
            == self.tofu_dishes_size
        )


class mandatory_FishDishes(BaseCondition):
    def __init__(self, fish_dishes_size: int = 1):
        self.fish_dishes_size = fish_dishes_size

    def satisfies_condition(self, meal_selection):
        return (
            sum(1 for dish in meal_selection if dish["protein"] == "Fish")
            == self.fish_dishes_size
        )


class mandatory_LegumeDishes(BaseCondition):
    def __init__(self, legume_dishes_size: int = 3):
        self.legume_dishes_size = legume_dishes_size

    def satisfies_condition(self, meal_selection):
        return (
            sum(1 for dish in meal_selection if dish.get("legume"))
            == self.legume_dishes_size
        )


class maximum_LegumeRepeated(BaseCondition):
    def __init__(self, maximum_repeated_legume: int = 1):
        self.maximum_repeated_legume = maximum_repeated_legume

    def satisfies_condition(self, meal_selection):
        legume_counter = {}
        for dish in meal_selection:
            legume = dish.get("legume")
            
            if legume:
                legume_counter[legume] = legume_counter.get(legume, 0) + 1
                
                if legume_counter[legume] > self.maximum_repeated_legume:
                    return False
                    
        return True