import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import words
from transformers import pipeline


class WebScrapeService:
    def __init__(self):
        # Download the NLTK 'words' corpus once during initialization
        nltk.download('words')

        # Initialize the classifier once for performance
        self.classifier = pipeline("text-classification",
                                   model="tanvircr7/learn_hf_food_not_food_text_classifier-distilbert-base-uncased")

    def getTitle(self, link: str):
        """Extracts a title from the URL based on its structure."""
        linksplit = link.split('/')
        filtered = []

        if linksplit[-1] == '':
            result = linksplit[len(linksplit) - 2]
        else:
            result = linksplit[-1]

        # Replace non-word characters with space and remove digits
        result = re.sub(r'\W+', ' ', result)
        result = re.sub(r'\d+', ' ', result)

        eng = set(words.words())  # Set of English words

        # Classify and filter words based on 'food' classification or valid English words
        for word in result.split():
            isfood = self.classifier(word)
            if word.lower() in eng or isfood[0]['label'] == 'food':
                filtered.append(word)

        # Return the filtered and joined result as the title
        result = ' '.join(filtered)
        return result

    def getInstructions(self, soup):
        """Extracts cooking instructions from the page and returns them as a list."""
        instructions = []

        # Find all instruction-related tags (li, span, div) with 'instruction' or 'direction' in the class name
        for instruction in soup.find_all(['li', 'span', 'div'],
                                         class_=lambda x: x and (
                                                 'instruction' in x.lower() or 'direction' in x.lower())):
            text = instruction.get_text().strip()  # Get the text and remove leading/trailing whitespace
            if text:
                instructions.append(text)  # Add non-empty instruction to the list

        # Debugging: Print the list of instructions before returning
        print(f"Instructions (as list): {instructions} -- Type: {type(instructions)}")

        return instructions  # Return the list of instructions

    def getIngredients(self, soup):
        """Extracts ingredients from the page."""
        ingredients = []
        for ingredient in soup.find_all(['li', 'span', 'div'],
                                        class_=lambda x: x and ('ingredient' in x.lower() or 'prep' in x.lower())):
            ingredients.append(ingredient.get_text())

        found = False
        recipe = "".join(ingredients)
        recipe = re.sub(r'[^\w\s]', '', recipe)
        recipe = re.sub(r'\s+', ' ', recipe).strip()

        # Insert spaces between capital and lowercase letters
        recipe = re.sub(r'(?<!\s)(?=[A-Z])', ' ', recipe)
        # Insert space between numbers and letters
        recipe = re.sub(r'(?<=\d)(?=[a-zA-Z])', ' ', recipe)
        recipe = re.sub(r'(?<=[a-zA-Z])(?=\d)', ' ', recipe)
        recipe = re.sub(r'(?<!\s)(?=[¼½¾⅛⅜⅝⅞])', ' ', recipe)

        # Debugging - print ingredients to check format
        print(f"Ingredients (after cleanup): {recipe}")

        ingredients = recipe.split(" ")
        if len(ingredients) > 50:
            templist, found = self.findWord("ingredient", ingredients, found)
            if not found:
                templist, found = self.findWord("prep", ingredients, found)

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
            ingredients = unique  # Keep as a list of ingredients

        # Debugging - print final ingredients to check
        print(f"Final Ingredients: {ingredients}")

        return ingredients  # Return as list of ingredients

    def findWord(self, word, ingredients, found):
        """Search for a word like 'ingredient' or 'prep' in the list."""
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
        return templist, found
