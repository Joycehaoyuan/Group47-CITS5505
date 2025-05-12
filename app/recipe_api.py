import os
import json
import requests
from typing import List, Dict, Any, Optional

# Get API key
RECIPE_API_KEY = os.environ.get('RECIPE_API_KEY')

def get_recipes_by_ingredients(ingredients: List[str], 
                              diet_type: Optional[str] = None, 
                              limit: int = 5) -> List[Dict[Any, Any]]:
    """
    Get recipe suggestions based on provided ingredients
    
    Parameters:
        ingredients: List of ingredients
        diet_type: Diet type (e.g. 'vegetarian', 'vegan', 'keto' etc.)
        limit: Number of recipes to return
        
    Returns:
        Recipe list
    """
    # Use Spoonacular API (can be replaced with other APIs)
    base_url = "https://api.spoonacular.com/recipes/findByIngredients"
    
    # Convert ingredients list to comma-separated string
    ingredients_str = ','.join(ingredients)
    
    # Build parameters
    params = {
        'apiKey': RECIPE_API_KEY,
        'ingredients': ingredients_str,
        'number': limit,  # Number of recipes to return
        'ranking': 2,  # Maximize use of provided ingredients
        'ignorePantry': True  # Ignore common ingredients like salt, oil, etc.
    }
    
    try:
        # Send request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # If request fails, raise an exception
        
        # Parse response
        recipes = response.json()
        
        # If diet type is specified, filter results
        if diet_type and diet_type.lower() != 'anything':
            # For each recipe, we need to get more detailed information to check if it matches the diet type
            filtered_recipes = []
            for recipe in recipes:
                recipe_id = recipe['id']
                recipe_info = get_recipe_details(recipe_id)
                
                # Check if the recipe matches the diet type
                if recipe_info and diet_type.lower() in (diet.lower() for diet in recipe_info.get('diets', [])):
                    filtered_recipes.append(recipe)
            
            return filtered_recipes
        
        return recipes
    
    except requests.exceptions.Timeout:
        print(f"API request timed out")
        return []
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return []

def get_recipes_by_ingredients(ingredients: List[str], 
                              diet_type: Optional[str] = None, 
                              limit: int = 5) -> List[Dict[Any, Any]]:
    """
    Get recipe suggestions based on provided ingredients
    
    Parameters:
        ingredients: List of ingredients
        diet_type: Diet type (e.g. 'vegetarian', 'vegan', 'keto' etc.)
        limit: Number of recipes to return
        
    Returns:
        Recipe list
    """
    # Use Spoonacular API (can be replaced with other APIs)
    base_url = "https://api.spoonacular.com/recipes/findByIngredients"
    
    # Get API key from environment
    api_key = os.environ.get('RECIPE_API_KEY')
    
    # If API key is not set, return an empty list
    if not api_key:
        print("API key not set. Please set RECIPE_API_KEY environment variable.")
        return []
    
    # Convert ingredients list to comma-separated string
    ingredients_str = ','.join(ingredients)
    
    # Build parameters
    params = {
        'apiKey': api_key,
        'ingredients': ingredients_str,
        'number': limit,  # Number of recipes to return
        'ranking': 2,  # Maximize use of provided ingredients
        'ignorePantry': True  # Ignore common ingredients like salt, oil, etc.
    }
    
    try:
        # Send request with a timeout
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # If request fails, raise an exception
        
        # Parse response
        recipes = response.json()
        
        # If diet type is specified, filter results
        if diet_type and diet_type.lower() != 'anything':
            # For each recipe, we need to get more detailed information to check if it matches the diet type
            filtered_recipes = []
            for recipe in recipes:
                recipe_id = recipe['id']
                recipe_info = get_recipe_details(recipe_id)
                
                # Check if the recipe matches the diet type
                if recipe_info and diet_type.lower() in (diet.lower() for diet in recipe_info.get('diets', [])):
                    filtered_recipes.append(recipe)
            
            return filtered_recipes
        
        return recipes
    
    except requests.exceptions.Timeout:
        print(f"API request timed out after 10 seconds")
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
    Search recipes based on query string
    
    Parameters:
        query: Search query string
        diet_type: Diet type (e.g. 'vegetarian', 'vegan', 'keto' etc.)
        cuisine: Cuisine type (e.g. 'italian', 'chinese', 'mexican' etc.)
        max_calories: Maximum calories per serving
        limit: Number of recipes to return
        
    Returns:
        Recipe list
    """
    url = "https://api.spoonacular.com/recipes/complexSearch"
    
    params = {
        'apiKey': RECIPE_API_KEY,
        'query': query,
        'number': limit,
        'addRecipeInformation': True,  # Include recipe information
        'fillIngredients': True,  # Include ingredient information
    }
    
    # Add optional parameters
    if diet_type and diet_type.lower() != 'anything':
        params['diet'] = diet_type.lower()
    
    if cuisine:
        params['cuisine'] = cuisine
    
    if max_calories:
        params['maxCalories'] = max_calories
    
    try:
        response = requests.get(url, params=params)
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
    Format recipe data for display
    
    Parameters:
        recipe: Original recipe data
        
    Returns:
        Formatted recipe data
    """
    # If the recipe is from findByIngredients
    if 'usedIngredients' in recipe:
        formatted = {
            'id': recipe.get('id'),
            'title': recipe.get('title'),
            'image': recipe.get('image'),
            'usedIngredients': [item.get('name') for item in recipe.get('usedIngredients', [])],
            'missedIngredients': [item.get('name') for item in recipe.get('missedIngredients', [])],
            'likes': recipe.get('likes', 0)
        }
        
        # Get full recipe information
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
    
    # If the recipe is from complexSearch
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