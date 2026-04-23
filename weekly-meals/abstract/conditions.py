class ConditionsManager:
    def __init__(self, plan_size, rules):
        self.meal_plan_size = plan_size
        self.rules = [Rule(rule_config) for rule_config in rules]

    @classmethod
    def from_profile(cls, profile):
        if "plan_size" not in profile:
            raise ValueError("Profile is missing required field 'plan_size'")

        return cls(plan_size=profile["plan_size"], rules=profile.get("rules", []))

    def check_conditions(self, meal_selection):
        if len(meal_selection) != self.meal_plan_size:
            return False

        return all(rule.is_satisfied(meal_selection) for rule in self.rules)

    def can_still_satisfy(self, meal_selection, remaining_dishes):
        if len(meal_selection) > self.meal_plan_size:
            return False

        if len(meal_selection) + len(remaining_dishes) < self.meal_plan_size:
            return False

        remaining_slots = self.meal_plan_size - len(meal_selection)
        return all(
            rule.can_still_satisfy(meal_selection, remaining_dishes, remaining_slots)
            for rule in self.rules
        )


class Rule:
    def __init__(self, config):
        self.rule_type = config.get("type")
        self.op = config.get("op")
        self.value = config.get("value")
        self.where = config.get("where")
        self.key = config.get("key")
        self.ignore_null = config.get("ignore_null", False)

        self._validate()

    def is_satisfied(self, meal_selection):
        if self.rule_type == "count":
            count = self._count_matches(meal_selection)
            return self._compare(count)

        if self.rule_type == "max_frequency":
            maximum = self._maximum_frequency(meal_selection)
            return self._compare(maximum)

        raise ValueError(f"Unsupported rule type: {self.rule_type}")

    def can_still_satisfy(self, meal_selection, remaining_dishes, remaining_slots):
        if self.rule_type == "count":
            current_count = self._count_matches(meal_selection)
            remaining_matching = self._count_matches(remaining_dishes)
            remaining_total = len(remaining_dishes)

            if self.op == "eq":
                if current_count > self.value:
                    return False

                required_matching = self.value - current_count
                if (
                    required_matching > remaining_matching
                    or required_matching > remaining_slots
                ):
                    return False

                remaining_nonmatching = remaining_total - remaining_matching
                required_nonmatching = remaining_slots - required_matching
                return required_nonmatching <= remaining_nonmatching

            if self.op == "gte":
                return current_count + remaining_matching >= self.value

            if self.op == "lte":
                return current_count <= self.value

        if self.rule_type == "max_frequency":
            return self.is_satisfied(meal_selection)

        raise ValueError(f"Unsupported rule type: {self.rule_type}")

    def _validate(self):
        if self.rule_type not in {"count", "max_frequency"}:
            raise ValueError(f"Unsupported rule type: {self.rule_type}")

        if self.rule_type == "count":
            if self.op not in {"eq", "gte", "lte"}:
                raise ValueError(f"Unsupported count operator: {self.op}")
            if not isinstance(self.value, int):
                raise ValueError("Count rules require an integer 'value'")
            if not isinstance(self.where, dict) or "attr" not in self.where:
                raise ValueError("Count rules require a 'where' selector with 'attr'")
            return

        if self.op != "lte":
            raise ValueError("max_frequency rules only support 'lte'")
        if not isinstance(self.value, int):
            raise ValueError("max_frequency rules require an integer 'value'")
        if not self.key:
            raise ValueError("max_frequency rules require a 'key'")

    def _compare(self, observed):
        if self.op == "eq":
            return observed == self.value
        if self.op == "gte":
            return observed >= self.value
        if self.op == "lte":
            return observed <= self.value
        raise ValueError(f"Unsupported operator: {self.op}")

    def _count_matches(self, dishes):
        return sum(1 for dish in dishes if self._matches(dish))

    def _matches(self, dish):
        attrs = dish.get("attrs", {})
        attr = self.where["attr"]
        attr_value = attrs.get(attr)

        if "eq" in self.where:
            return attr_value == self.where["eq"]

        if "in" in self.where:
            return attr_value in self.where["in"]

        if "exists" in self.where:
            return (attr_value is not None) == bool(self.where["exists"])

        raise ValueError(f"Unsupported selector for attribute '{attr}'")

    def _maximum_frequency(self, dishes):
        frequencies = {}

        for dish in dishes:
            attr_value = dish.get("attrs", {}).get(self.key)
            if attr_value is None and self.ignore_null:
                continue

            frequencies[attr_value] = frequencies.get(attr_value, 0) + 1

        return max(frequencies.values(), default=0)
