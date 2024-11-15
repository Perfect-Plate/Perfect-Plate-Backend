import re  # RegEX
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import json
import nltk
from nltk.corpus import words


# REFERENCES:
# https://huggingface.co/docs/transformers/quicktour
# https://huggingface.co/tanvircr7/learn_hf_food_not_food_text_classifier-distilbert-base-uncased?library=transformers

nltk.download('words')
classifier = pipeline("text-classification",model="tanvircr7/learn_hf_food_not_food_text_classifier-distilbert-base-uncased")
class WebScraper:
    def toJson(string):
        try:
            strings = string + ""
            json_start = strings.find('{')
            json_end = strings.rfind('}') + 1
            json_string = strings[json_start:json_end]


            json_object = json.loads(json_string)
            formatted_json_string = json.dumps(json_object, indent=4)
            return formatted_json_string
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
        templist = []
        startat = 0
        found = False
        recipe = "".join(ingredients)
        recipe = re.sub(r'[^\w\s]', '', recipe)
        recipe = re.sub(r'\s+', ' ', recipe).strip()

        ingredients = recipe.split(" ")
        if(len(ingredients) > 125):
            for i in range(len(ingredients)-1,-1,-1):
                if "ingredient" in ingredients[i].lower():
                    if(len(ingredients) - i) > 30:
                        found = True
                        startat = i
                        ingredients[i] = "Ingredients:"
                    continue
                if found:
                    break
            if found:
                for j in range(startat,len(ingredients)):
                    templist.append(ingredients[j])
        ingredients = templist

        # Split link by commas
        linksplit = link.split('/')
        print(linksplit)

        filtered = []
        result = linksplit[len(linksplit)-2]
        result = re.sub(r'\d', ' ', result)
        result = re.sub(r'-', ' ', result)
        eng = set(words.words())
        print(result)
        for word in result:
            isfood = classifier(word)
            print(word)
            print(isfood)
            if word.lower() in eng or isfood[0]['label'] == 'food':
                filtered.append(word)


        result = ''.join(filtered)

        return ingredients, result

if __name__ == '__main__':
    app = WebScraper
    ingredientlist,result = app.scrapeWeb("https://www.mccormick.com/recipes/breakfast-brunch/tropical-acai-bowl?msockid=3218975560e56c103fc78264616f6da5")
    recipe = " ".join(ingredientlist)
    prompt = f'''
    Please provide a high protien recipe for {result} in the following format:
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
    Using this recipe as a baseline: {recipe}
    '''
    print(prompt)
    print(recipe)
    print(result)
    genai.configure(api_key="APIKEY")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    print(response.text)
    jsonHolder = app.toJson(response.text)
    print("JSON:")
    print(jsonHolder)