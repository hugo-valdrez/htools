# weekly_meals

This one generates a weekly meal plan from the files in `configs/`.

It reads:
- `dishes.yaml` for the available dishes
- `conditions.yaml` for the rules and profiles
- `history.yaml` to avoid repeating the same stuff too often

Run it with:

```bash
htools weekly-meals
```

Or pick a specific profile:

```bash
htools weekly-meals default
```

Notes:
- the default profile comes from `configs/conditions.yaml`
- after generating a plan, it can optionally save it to history
- the output is just a terminal summary, nothing fancy
