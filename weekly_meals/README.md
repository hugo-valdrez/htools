# weekly-meals

So, I'm trying to turn my weekly meal planning into a problem, it goes like this:

- Every meal is divided into 4 things:
    1. The type of hidrates (Rice, Pasta, Potatoes, Bread, etc...)
    2. The type of protein (Soy, Fish, Tofu, Eggs, etc...)
    3. If it has legumes or not (Beans, Lentils, etc...), it's binary.
    4. An unique identifier, because some dishes might have the same combination of 1, 2 and 3 but be cooked in a different way, therefore a different dish.


Given a list of different meals with the above points defined for each one, example:
```
- Bologense -> (1,1,0,1)
    - Pasta (1)
    - Meat (1)
    - No (0)
    - Bolognese (1)

- Carbonara -> (1,1,0,2)
    - Pasta (1)
    - Meat (1)
    - No (0)
    - Carbonara (2)
```


And given a list of conditions to be satisfied:
```
1. Number of dishes = 7
2. Minimum number of dishes with pasta = 1
3. Minimum number of dishes with rice = 1
4. Minimum number of dishes with potatoes = 1
5. Number of dishes with tofu = 2
6. Number of dishes with legumes = 3
7. Number of dishes with fish = 1
```


I want to be able to generate a meal plan. Help me out formalize this problem and solve it. In the end, I'll write code to run it on a weekly basis. 

Mathematically, this is a **Constraint Satisfaction Problem (CSP)** or, more specifically, a **0-1 Integer Linear Programming (ILP)** problem. We are trying to select a subset of items (dishes) from a larger set that satisfies a specific group of linear constraints. Let's now formalize this problem.

## 1. Formalization of the Problem

### The Variables

Let $D$ be the set of all available dishes in your database.
For each dish $i \in D$, we define a binary decision variable $x_i$:
- $x_i = 1$ if dish $i$ is selected for the weekly plan.
- $x_i = 0$ otherwise.
    
### The Parameters
Each dish $i$ has attributes based on our 4-tuple $(H, P, L, ID)$:
- $H_{i, \text{type}}$: The carbohydrate type (e.g., $1$ for Pasta, $2$ for Rice).
- $P_{i, \text{type}}$: The protein type (e.g., $1$ for Meat, $2$ for Tofu, $3$ for Fish).
- $L_i$: A binary value ($1$ if it has legumes, $0$ if not).
    

### The Constraints
Based on our rules, we can write the following equations:

1. **Total Count:** $\sum_{i \in D} x_i = 7$
2. **Min Pasta:** $\sum_{i \in D, H_i=1} x_i \ge 1$
3. **Min Rice:** $\sum_{i \in D, H_i=2} x_i \ge 1$
4. **Min Potatoes:** $\sum_{i \in D, H_i=3} x_i \ge 1$
5. **Tofu Count:** $\sum_{i \in D, P_i=2} x_i = 2$
6. **Legume Count:** $\sum_{i \in D, L_i=1} x_i = 3$
7. **Fish Count:** $\sum_{i \in D, P_i=3} x_i = 1$
    