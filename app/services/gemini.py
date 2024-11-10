import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import re  # RegEX
from transformers import pipeline


# REFERENCES:
# https://huggingface.co/docs/transformers/quicktour
# https://huggingface.co/tanvircr7/learn_hf_food_not_food_text_classifier-distilbert-base-uncased?library=transformers

def geminiCreateRecipe(link):
    # Case of blacklist (Not direction of project, but kept in for demonstration purposes)
    nuts = ["Almonds", "Cashews", "Walnuts", "Pecans", "Pistachios", "Hazelnuts", "Brazil nuts", "Macadamia nuts",
            "Pine nuts", "Chestnuts"]
    blacklist = "Blacklist the following allergies in the response: """ + ", ".join(nuts)

    response = requests.get(link)  # Send Request
    ingredients = []  # Initialized Array

    print(f'Status Code: {response.status_code}')  # Formatting in output, don't need later

    if response.status_code == 200:  # Successfully got response from site

        # CASE 1: Webscrape the data, isolate the ingredients, prompt the LLM
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for ingredients in all places should be. Add to Array
        for ingredient in soup.find_all(['li', 'span', 'div'],
                                        class_=lambda x: x and ('ingredient' in x.lower() or 'prep' in x.lower())):
            ingredients.append(ingredient.get_text())

        # Blacklist + Prompt + Recipe
        prompt = blacklist + """
        Please provide a recipe in the following format:

        *Name of recipe

        Ingredients:
        - List of ingredients

        Instructions:
        1. Step-by-step instructions

        Recipe:*

        Using this recipe as a baseline: """ + ", ".join(ingredients)
        return prompt
    else:
        # CASE 2: Connection Interruption OR Blocked Scraper
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
            if result[0]['label'] == 'food':
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

        prompt = blacklist + """

        Please provide a recipe for """ + result + """ in the following format:

        Name of recipe

        Ingredients:
        - List of ingredients

        Instructions:
        1. Step-by-step instructions

        Recipe:
        """
        return prompt


genai.configure(
    api_key="API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")  # Model

# CASE 1: WebScraping
print("Case 1: WebScraping" + "\n" + "\n" + "\n")  # Formatting
prompt = geminiCreateRecipe("https://cafedelites.com/quick-easy-creamy-herb-chicken/")  # Satus Code: 200 in most cases
print(prompt)  # Prompt Display
response = model.generate_content(prompt)  # Generate using formatted prompt
print(response.text)  # Display as text

# CASE 2: Status Code != 200, So we use the link differently
print("==============================================================================================")  # Formatting
print("Case 2: Link Parsing" + "\n" + "\n" + "\n")  # Formatting
prompt = geminiCreateRecipe(
    "https://www.foodnetwork.com/recipes/food-network-kitchen/air-fryer-acorn-squash-with-brown-butter-9335917")  # Will give 403
print(prompt)  # Prompt Display
response = model.generate_content(prompt)  # Generate using formatted prompt
print(response.text)  # Display as text

# Pydantic Formatting to JSON to control what goes to the front end