"""
bmi_logic.py - Pure calculation logic for the BMI Calculator (Advanced Tier)
-------------------------------------------------------------------------------
Kept separate from the GUI and database code so the math can be tested
on its own, without needing a window or a database.
"""


def calculate_bmi(weight_kg, height_m):
    """BMI = weight (kg) / height (m) squared."""
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi):
    """Turn a BMI number into a health category label."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def category_color(category):
    """Map each category to a colour for the GUI result label."""
    return {
        "Underweight": "#3B82F6",  # blue
        "Normal": "#22C55E",       # green
        "Overweight": "#F59E0B",   # amber
        "Obese": "#EF4444",        # red
    }.get(category, "#000000")
