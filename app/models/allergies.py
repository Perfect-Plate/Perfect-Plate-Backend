from dataclasses import dataclass


@dataclass
class Allergies:
    allergy1: str
    allergy2: str
    allergy3: str
    allergy4: str
    allergy5: str


# Testing Allergies
allergiesEX = Allergies(
    allergy1="Peanuts",
    allergy2="Fish",
    allergy3="Lactose",
    allergy4="Bison",
    allergy5="Green Onions",
)
print(allergiesEX)
