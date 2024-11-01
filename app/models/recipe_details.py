from typing import List
from dataclasses import dataclass

@dataclass
class RecipeDetails:
    Name: str  # EG: Spaghetti Carbonara
    Ingredients: List[str]  # Array, with each ingredient. As list because each recipe will vary in number of ingredients.
    Instructions: str  # For the instructions.
    Image: str  # Link to image

#
# if __name__ == "__main__":
#     import uvicorn
#
#     rd = RecipeDetails(Name="banana", Ingredients=["peel,banana,yellow"], Instructions="Peel banana, Eat banana",
#                        Image="https://th.bing.com/th/id/R.0f3cc1b69f7046e6355687263aead9ee?rik=e%2fzLRdxmCMtNRA&riu=http%3a%2f%2fupload.wikimedia.org%2fwikipedia%2fcommons%2f6%2f69%2fBanana.png&ehk=0MA9r3huU44GTjIIWGK6A1R0At%2bSPNmztxBBWKsquWw%3d&risl=1&pid=ImgRaw&r=0")
#
#     create_recipe_details(rd)
#     uvicorn.run(app, host="0.0.0.0", port=8000)
