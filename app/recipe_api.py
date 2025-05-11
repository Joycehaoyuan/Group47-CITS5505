import os
import json
import requests
from typing import List, Dict, Any, Optional

# Get API key from environment
RECIPE_API_KEY = os.environ.get('RECIPE_API_KEY')


def get_recipes_by_ingredients(ingredients: List[str], 
                                diet_type: Optional[str] = None, 
                                limit: int = 5) -> List[Dict[Any, Any]]:
    """
    Get recipe suggestions based on provided ingredients.
    """
    base_url = "https://api.spoonacular.com/recipes/findByIngredients"

    if not RECIPE_API_KEY:
        print("API key not set. Please set RECIPE_API_KEY environment variable.")
        return []

    ingredients_str = ','.join(ingredients)

    params = {
        'apiKey': RECIPE_API_KEY,
        'ingredients': ingredients_str,
        'number': limit,
        'ranking': 2,
        'ignorePantry': True
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        recipes = response.json()

        if diet_type and diet_type.lower() != 'anything':
            filtered_recipes = []
            for recipe in recipes:
                recipe_id = recipe['id']
                recipe_info = get_recipe_details(recipe_id)
                if recipe_info and diet_type.lower() in (d.lower() for d in recipe_info.get('diets', [])):
                    filtered_recipes.append(recipe)
            return filtered_recipes

        return recipes

    except requests.exceptions.Timeout:
        print("API request timed out after 10 seconds")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return []
    except json.JSONDecodeError:
        print("JSON parsing error")
        return []


def search_recipes(query: str, 
                   diet_type: Optional[str] = None,
                   cuisine: Optional[str] = None,
                   max_calories: Optional[int] = None,
                   limit: int = 5) -> List[Dict[Any, Any]]:
    """
    Search recipes based on a keyword.
    """
    base_url = "https://api.spoonacular.com/recipes/complexSearch"

    if not RECIPE_API_KEY:
        print("API key not set. Please set RECIPE_API_KEY environment variable.")
        return []

    params = {
        'apiKey': RECIPE_API_KEY,
        'query': query,
        'number': limit,
        'addRecipeInformation': True,
        'fillIngredients': True
    }

    if diet_type and diet_type.lower() != 'anything':
        params['diet'] = diet_type.lower()

    if cuisine:
        params['cuisine'] = cuisine

    if max_calories:
        params['maxCalories'] = max_calories

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()
        return result.get('results', [])
    
    except requests.exceptions.RequestException as e:
        print(f"Error searching recipes: {e}")
        return []
    except json.JSONDecodeError:
        print("JSON parsing error")
        return []


def format_recipe_for_display(recipe: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Format recipe data from API response for frontend display.
    """
    if 'usedIngredients' in recipe:
        formatted = {
            'id': recipe.get('id'),
            'title': recipe.get('title'),
            'image': recipe.get('image'),
            'usedIngredients': [item.get('name') for item in recipe.get('usedIngredients', [])],
            'missedIngredients': [item.get('name') for item in recipe.get('missedIngredients', [])],
            'likes': recipe.get('likes', 0)
        }

        recipe_id = recipe.get('id')
        if recipe_id is not None:
            details = get_recipe_details(int(recipe_id))
            if details:
                formatted.update({
                    'instructions': details.get('instructions'),
                    'readyInMinutes': details.get('readyInMinutes'),
                    'servings': details.get('servings'),
                    'sourceUrl': details.get('sourceUrl'),
                    'summary': details.get('summary'),
                    'diets': details.get('diets', []),
                    'nutrition': details.get('nutrition', {})
                })

        return formatted

    else:
        return {
            'id': recipe.get('id'),
            'title': recipe.get('title'),
            'image': recipe.get('image'),
            'readyInMinutes': recipe.get('readyInMinutes'),
            'servings': recipe.get('servings'),
            'sourceUrl': recipe.get('sourceUrl'),
            'summary': recipe.get('summary'),
            'diets': recipe.get('diets', []),
            'instructions': recipe.get('instructions'),
            'extendedIngredients': [
                {
                    'name': ing.get('name'),
                    'amount': ing.get('amount'),
                    'unit': ing.get('unit')
                } for ing in recipe.get('extendedIngredients', [])
            ]
        }
