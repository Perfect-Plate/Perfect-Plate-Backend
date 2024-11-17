import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import words
from transformers import pipeline

class nabtesting:
    def nab(url: str):
        HEADER = {"User-Agent": "Mozilla/5.0"}  # Prevents blocks on certain sites
        response = requests.get(url, headers=HEADER)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(response.status_code)

        # Print the HTML content for debugging
        # print(soup.prettify())

        # Adjust the selector based on the actual structure of the page
        recipes = soup.find_all('div', class_='recipe')
        current_time = datetime.now()

        # Debug print to check if recipes are found
        # print(f"Found {len(recipes)} recipes")
        title = getTitle(url)
        ingredients = getIngredients(soup)
        description = soup.find('p', class_='description')
        if description == '':
            description = f"A delicious {title}"
        instructions = getInstructions(soup)

        return {
             "title": title,
             "description": description,
             "ingredients": ingredients,
             "instructions": instructions,
             "created_at": current_time,
             "updated_at": current_time,
             "date_added": current_time.date(),
             "date_updated": current_time.date()
        }

    def getTitle(link):
        nltk.download('words')
        classifier = pipeline("text-classification",
                              model="tanvircr7/learn_hf_food_not_food_text_classifier-distilbert-base-uncased")
        linksplit = link.split('/')

        filtered = []
        if linksplit[-1] == '':
            result = linksplit[len(linksplit) - 2]
        else:
            result = linksplit[-1]
        # Replace non-word characters with space
        result = re.sub(r'\W+', ' ', result)
        result = re.sub(r'\d+', ' ', result)
        eng = set(words.words())

        for word in result.split():
            isfood = classifier(word)
            if word.lower() in eng or isfood[0]['label'] == 'food':
                filtered.append(word)

        result = ' '.join(filtered)
        return result

    def getInstructions(soup):
        instructions = []
        for instruction in soup.find_all(['li', 'span', 'div'],
                                        class_=lambda x: x and ('instruction' in x.lower() or 'direction' in x.lower())):
            instructions.append(instruction.get_text())
        recipe = "".join(instructions)
        recipe = re.sub(r'[^\w\s]', '', recipe)
        recipe = re.sub(r'\s+', ' ', recipe).strip()
        # Insert a space between capital and lowercase letters
        recipe = re.sub(r'(?<!\s)(?=[A-Z])', ' ', recipe)
        # Insert a space between numbers and letters
        recipe = re.sub(r'(?<=\d)(?=[a-zA-Z])', ' ', recipe)
        recipe = re.sub(r'(?<=[a-zA-Z])(?=\d)', ' ', recipe)
        recipe = re.sub(r'(?<!\s)(?=[¼½¾⅛⅜⅝⅞])', ' ', recipe)


        return recipe

    def getIngredients(soup):
        ingredients = []
        for ingredient in soup.find_all(['li', 'span', 'div'],
                                        class_=lambda x: x and ('ingredient' in x.lower() or 'prep' in x.lower())):
            ingredients.append(ingredient.get_text())

        found = False
        recipe = "".join(ingredients)
        recipe = re.sub(r'[^\w\s]', '', recipe)
        recipe = re.sub(r'\s+', ' ', recipe).strip()
        # Insert a space between capital and lowercase letters
        recipe = re.sub(r'(?<!\s)(?=[A-Z])', ' ', recipe)
        # Insert a space between numbers and letters
        recipe = re.sub(r'(?<=\d)(?=[a-zA-Z])', ' ', recipe)
        recipe = re.sub(r'(?<=[a-zA-Z])(?=\d)', ' ', recipe)
        recipe = re.sub(r'(?<!\s)(?=[¼½¾⅛⅜⅝⅞])', ' ', recipe)

        ingredients = recipe.split(" ")
        if (len(ingredients) > 50):
            templist,found = findWord("ingredient",ingredients,found)
            if not found:
                templist, found = findWord("prep", ingredients, found)
        if found:
            segments = " ".join(templist)
            unspacedSegs = re.sub(r'\s+', '', segments)
            unspacedSegs = re.split(r'(?=\d+|[¼½¾⅛⅜⅝⅞]|\d+ [¼½¾⅛⅜⅝⅞])', unspacedSegs)
            spacedSegs = re.split(r'(?=\d+|[¼½¾⅛⅜⅝⅞]|\d+ [¼½¾⅛⅜⅝⅞])', segments)
            seen = set()
            unique = []
            for i in range(len(unspacedSegs)):
                if unspacedSegs[i] not in seen:
                    seen.add(unspacedSegs[i])
                    unique.append(spacedSegs[i])
            ingredients = " ".join(unique)
        return ingredients

    def findWord(word,ingredients,found):
        templist = []
        startat = 0
        for i in range(len(ingredients) - 1, -1, -1):
            if word in ingredients[i].lower():
                if (len(ingredients) - i) > 30:
                    found = True
                    startat = i
                    ingredients[i] = "Ingredients:"
                continue
            if found:
                break
        if found:
            for j in range(startat, len(ingredients)):
                templist.append(ingredients[j])
        return templist,found

if __name__ == "__main__":
    n = nabtesting
    print(n.nab("https://www.purewow.com/recipes/avocado-chicken-salad"))
