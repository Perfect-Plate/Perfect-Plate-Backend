import re  # RegEX
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import json


# REFERENCES:
# https://huggingface.co/docs/transformers/quicktour
# https://huggingface.co/tanvircr7/learn_hf_food_not_food_text_classifier-distilbert-base-uncased?library=transformers

class WebScraper:
    def toJson(string):
        try:
            return json.loads(string)
        except:
            print("Error")
            return None

    def scrapeWeb(link):
        HEADER = {"User-Agent": "Mozilla/5.0"} #Prevents blocks on certain sites
        response = requests.get(link, headers=HEADER)  # Send Request
        ingredients = []  # Initialized Array

        print(f'Status Code: {response.status_code}')  # Formatting in output, don't need later

        if response.status_code == 200:  # Successfully got response from site

            # CASE 1: Webscrape the data, isolate the ingredients, prompt the LLM
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for ingredients in all places should be. Add to Array
            for ingredient in soup.find_all(['li', 'span', 'div'],
                                            class_=lambda x: x and ('ingredient' in x.lower() or 'prep' in x.lower())):
                ingredients.append(ingredient.get_text())

        classifier = pipeline("text-classification",
                                  model="tanvircr7/learn_hf_food_not_food_text_classifier-distilbert-base-uncased")
        # Split link by commas
        linksplit = link.split('/')

        # Initialize an empty list to store extracted food terms
        extracted = []
        probabilities = []
        # Check each word for food-related classification
        for word in linksplit:
            result = classifier(word)
            if result[0]['label'] == 'food' & word != "food" & word != "recipe" & word != "recipes":
                extracted.append(word)
                probabilities.append(result[0]['score'])

            # Loop to determine which of the 'food' words is the most likely to be related to the recipe
        largest = 0
        for i in range(len(probabilities)):
            if (probabilities[i] > probabilities[largest]):
                largest = i
        result = extracted[largest]
        result = re.sub(r'\d', '', result)
        result = re.sub(r'-', ' ', result)

        return ingredients, result

if __name__ == '__main__':
    app = WebScraper
    ingredients,result = app.scrapeWeb("https://www.hiddenvalley.com/recipe/glazed-hidden-valley-ham/")
    recipe = "".join(ingredients)
    recipe = re.sub(r'[^\w\s]','',recipe)
    recipe = re.sub(r'\s+',' ',recipe)
    recipe = recipe.strip()
    prompt = f'''
    Please provide a recipe for {result} in the following format, without including ANYTHING else in the response:
    {{
      "recipename": "Your Recipe Name Here",
      "ingredients": [
        "List of ingredients here",
        "Example: 1 cup flour",
        "Example: 2 eggs"
      ],
      "instructions": [
        "Step-by-step instructions here",
        "Example: Preheat oven to 350 degrees F (175 degrees C).",
        "Example: Mix flour and sugar."
      ],
      "recipe": "Detailed or summarized recipe description here."
    }}
    Using this recipe as a baseline: {", ".join(ingredients)}
    '''
    # print(prompt)
    print(recipe)
    print(result)
    genai.configure(api_key="AIzaSyBmkA7aY9ZwTWCHhGaeZlw1o-UQ0ibR2gU")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    print(response.text)
    jsonHolder = app.toJson(response.text)
    print(jsonHolder)