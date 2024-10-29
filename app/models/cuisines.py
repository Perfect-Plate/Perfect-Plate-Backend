from dataclasses import dataclass, field
from typing import List


@dataclass
class Cuisines:
    like: List[str] = field(default_factory=list)
    dislike: List[str] = field(default_factory=list)


# # Example
# cuisinesEX = Cuisines(
#     like=["Italian", "Japanese", "Mexican"],
#     dislike=["American", "Chinese"]
# )
# print(cuisinesEX)
