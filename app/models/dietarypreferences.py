from dataclasses import dataclass


@dataclass
class DietaryPreferences:
    None_Necessary: bool  # If this is true, then every other one should be false (Done in post, not in class).
    keto: bool
    paleo: bool
    vegetarian: bool
    vegan: bool
    pescatarian: bool


# Example
preferencesEX = DietaryPreferences(
    None_Necessary=False,
    keto=True,
    paleo=True,
    vegetarian=True,
    vegan=True,
    pescatarian=True
)
print(preferencesEX)
