import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import words
from transformers import pipeline

class WebScrapeService:
    @classmethod
    def getTitle(self,link):
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

    @classmethod
    def getInstructions(self,soup):
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

    @classmethod
    def getIngredients(self,soup):
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
            templist,found = self.findWord("ingredient",ingredients,found)
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
            ingredients = " ".join(unique)
        return ingredients

    @classmethod
    def findWord(self,word,ingredients,found):
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