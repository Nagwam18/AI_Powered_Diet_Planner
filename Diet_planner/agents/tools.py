import requests
from crewai.tools import BaseTool
import os
import json

class SpoonacularTool(BaseTool):
    name: str = "Spoonacular Recipe Finder"
    description: str = "Finds simple meal ingredient suggestions using Spoonacular API based on diet type, calories, and allergies."

    def _run(self, query: str) -> str:
        api_key = os.getenv("SPOONACULAR_API_KEY")
        if not api_key:
            return json.dumps([{"error": "Spoonacular API key not found in environment variables."}])

        try:
            query_data = json.loads(query)
        except json.JSONDecodeError:
            query_data = {"query": query}

        # Extract values from query
        keyword = query_data.get("query", "")
        diet_type = query_data.get("diet", "")
        intolerances = query_data.get("allergy", "")  # or 'intolerances'
        max_calories = query_data.get("calories", "")

        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "query": keyword,
            "number": 5,
            "addRecipeNutrition": True,
            "addRecipeInformation": True,
            "apiKey": api_key,
            "diet": diet_type,
            "intolerances": intolerances,
            "maxCalories": max_calories
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return json.dumps([{
                "error": f"Error from Spoonacular API: {response.status_code} - {response.text}"
            }])

        data = response.json()
        results = data.get("results", [])
        if not results:
            return json.dumps([{"error": "No recipe found."}])

        recipes = []
        for recipe in results:
            nutrients = recipe.get("nutrition", {}).get("nutrients", [])

            def get_nutrient(name):
                for n in nutrients:
                    if n["name"].lower() == name.lower():
                        return n["amount"]
                return "N/A"

            recipes.append({
                "title": recipe.get("title"),
                "link": recipe.get("sourceUrl"),
                "calories": get_nutrient("Calories"),
                "protein": get_nutrient("Protein"),
                "carbs": get_nutrient("Carbohydrates"),
                "fats": get_nutrient("Fat")
            })

        return json.dumps(recipes)
