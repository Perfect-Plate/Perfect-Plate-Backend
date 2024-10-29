from dataclasses import dataclass


@dataclass
class Nutrition:
    None_Necessary: bool  # If this is true, then every other one should be false (Done in post, not in class).
    LowCarb: bool
    HighProtein: bool
    LowFat: bool
    LowSodium: bool
    LowCalorie: bool


# # Testing
# nutritionEX = Nutrition(
#     None_Necessary=False,
#     LowCarb=True,
#     HighProtein=False,
#     LowFat=True,
#     LowSodium=False,
#     LowCalorie=True
# )
# print(nutritionEX)
