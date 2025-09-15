# Examples
## EXAMPLE 1:
Natural Language Query: "pizzas with cheese or mushroom toppings"

Validated Entities:
```
{{
  "classes": {{
    "pizza": {{"label": "Pizza"}},
    "cheese": {{"label": "Cheese"}},
    "mushroom": {{"label": "Mushroom"}}
  }},
  "properties": {{
    "hasTopping": {{"label": "hasTopping"}}
  }}
}}
```
Resulting Manchester Expression:

Pizza and (hasTopping some (Cheese or Mushroom))

## EXAMPLE 2:
Natural Language Query: "cars with exactly 4 wheels"
Validated Entities:
```
{{
  "classes": {{
    "car": {{"label": "Car"}},
    "wheel": {{"label": "Wheel"}}
  }},
  "properties": {{
    "hasPart": {{"label": "hasPart"}}
  }}
}}
```
Resulting Manchester Expression:
Car and (hasPart exactly 4 Wheel)

## EXAMPLE 3:
Natural Language Query: "red or blue vehicles"

Validated Entities:
```
{{
  "classes": {{
    "vehicle": {{"label": "Vehicle"}},
    "red": {{"label": "Red"}},
    "blue": {{"label": "Blue"}}
  }},
  "properties": {{}}
}}
```
Resulting Manchester Expression:

Vehicle and (Red or Blue)

## EXAMPLE 4:
Natural Language Query: "animals that eat only plants"
Validated Entities:
```
{{
  "classes": {{
    "animal": {{"label": "Animal"}},
    "plant": {{"label": "Plant"}}
  }},
  "properties": {{
    "eats": {{"label": "eats"}}
  }}
}}
```
Resulting Manchester Expression:

Animal and (eats only Plant)
Animal and (eats only Plant)
Resulting Manchester Expression:
