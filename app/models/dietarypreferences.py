from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class DietaryPreferences(BaseModel):
    None_Necessary: bool  # If this is true, then every other one should be false (Done in post, not in class).
    keto: bool
    paleo: bool
    vegetarian: bool
    vegan: bool
    pescatarian: bool

# def create_preference(preference: DietaryPreferences)
# # # Example
# # preferencesEX = DietaryPreferences(
# #     None_Necessary=False,
# #     keto=True,
# #     paleo=True,
# #     vegetarian=True,
# #     vegan=True,
# #     pescatarian=True
# # )
# # print(preferencesEX)
