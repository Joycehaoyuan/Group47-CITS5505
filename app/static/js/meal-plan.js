// Meal Plan generation and management functionality

document.addEventListener('DOMContentLoaded', function() {
    // Recipe suggestion button functionality
    const recipeSuggestionButtons = document.querySelectorAll('.recipe-suggestion-btn');
    if (recipeSuggestionButtons.length > 0) {
        recipeSuggestionButtons.forEach(button => {
            button.addEventListener('click', function() {
                const mealName = this.getAttribute('data-meal-name');
                const foodsString = this.getAttribute('data-foods');
                const foods = foodsString.split(',').map(food => food.trim());
                
                showRecipeSuggestions(mealName, foods);
            });
        });
    }
    
    // Function to show recipe suggestions modal
    function showRecipeSuggestions(mealName, foods) {
        // Create modal if it doesn't exist
        let recipeSuggestionsModal = document.getElementById('recipeSuggestionsModal');
        if (!recipeSuggestionsModal) {
            const modalHtml = `
                <div class="modal fade" id="recipeSuggestionsModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Recipe Suggestions for <span id="recipe-meal-name"></span></h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div id="recipe-suggestions-content">
                                    <div class="mb-4">
                                        <h6>Ingredients</h6>
                                        <ul id="recipe-ingredients" class="list-group list-group-flush"></ul>
                                    </div>
                                    <div id="recipes-loading" class="text-center py-4">
                                        <div class="spinner-border text-success" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                        <p class="mt-2">Generating recipe suggestions...</p>
                                    </div>
                                    <div id="recipe-content" style="display:none;">
                                        <h6>Suggested Recipes</h6>
                                        <div id="recipe-list" class="mt-3"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            recipeSuggestionsModal = document.getElementById('recipeSuggestionsModal');
        }
        
        // Update modal content
        document.getElementById('recipe-meal-name').textContent = mealName;
        
        // Display ingredients
        const ingredientsList = document.getElementById('recipe-ingredients');
        ingredientsList.innerHTML = '';
        foods.forEach(food => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = food;
            ingredientsList.appendChild(li);
        });
        
        // Show loading
        const recipesLoading = document.getElementById('recipes-loading');
        const recipeContent = document.getElementById('recipe-content');
        if (recipesLoading) recipesLoading.style.display = 'block';
        if (recipeContent) recipeContent.style.display = 'none';
        
        // Show the modal
        const modal = new bootstrap.Modal(recipeSuggestionsModal);
        modal.show();
        
        // Get recipe suggestions from API
        fetch('/api/recipe-suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                foods: foods,
                meal_name: mealName
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading and show content
            if (recipesLoading) recipesLoading.style.display = 'none';
            if (recipeContent) recipeContent.style.display = 'block';
            
            // Generate recipe suggestions
            const recipeList = document.getElementById('recipe-list');
            recipeList.innerHTML = '';
            
            if (data.success && data.recipes && data.recipes.length > 0) {
                data.recipes.forEach(recipe => {
                    const recipeCard = document.createElement('div');
                    recipeCard.className = 'card mb-3';
                    
                    recipeCard.innerHTML = `
                        <div class="card-header">
                            <h5 class="card-title mb-0">${recipe.name}</h5>
                        </div>
                        <div class="card-body">
                            <h6>Ingredients:</h6>
                            <ul class="mb-3">
                                ${recipe.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('')}
                            </ul>
                            <h6>Instructions:</h6>
                            <ol>
                                ${recipe.instructions.map(step => `<li>${step}</li>`).join('')}
                            </ol>
                        </div>
                    `;
                    
                    recipeList.appendChild(recipeCard);
                });
            } else {
                // No recipes found or error
                recipeList.innerHTML = '<div class="alert alert-info">No recipe suggestions found for these ingredients.</div>';
            }
        })
        .catch(error => {
            console.error('Error getting recipe suggestions:', error);
            
            // Hide loading and show content with error
            if (recipesLoading) recipesLoading.style.display = 'none';
            if (recipeContent) recipeContent.style.display = 'block';
            
            const recipeList = document.getElementById('recipe-list');
            recipeList.innerHTML = '<div class="alert alert-danger">Error loading recipe suggestions. Please try again later.</div>';
        });
    }
    
    // Function to generate recipe suggestions based on ingredients
    function generateRecipeSuggestions(foods) {
        // Simple logic to create recipe suggestions based on available ingredients
        const recipes = [];
        
        console.log("Got foods:", foods);
        
        // Convert foods to lowercase for easier matching
        const foodsLower = foods.map(food => food.toLowerCase());
        
        // Check for common combinations and suggest recipes
        
        // Eggs recipe
        if (foodsLower.some(food => food.includes('egg'))) {
            recipes.push({
                name: "Simple Scrambled Eggs",
                ingredients: [
                    "3 large eggs",
                    "1 tbsp butter or oil",
                    "Salt and pepper to taste",
                    "Optional: chopped herbs, cheese, or vegetables"
                ],
                instructions: [
                    "Beat eggs in a bowl with a pinch of salt and pepper.",
                    "Heat butter or oil in a non-stick pan over medium heat.",
                    "Pour in eggs and cook, stirring gently until they begin to set.",
                    "When eggs are mostly set but still slightly wet, remove from heat (they will continue cooking).",
                    "Add any optional ingredients like herbs or cheese, and serve immediately."
                ]
            });
        }
        
        // Vegetable frittata recipe
        if (foodsLower.some(food => food.includes('frittata') || food.includes('vegetable'))) {
            recipes.push({
                name: "Vegetable Frittata",
                ingredients: [
                    "6 large eggs",
                    "1/4 cup milk or cream",
                    "1 cup mixed vegetables (spinach, bell peppers, onions, etc.)",
                    "1/4 cup grated cheese",
                    "1 tbsp olive oil",
                    "Salt and pepper to taste"
                ],
                instructions: [
                    "Preheat oven to 375°F (190°C).",
                    "Whisk eggs, milk, salt, and pepper in a bowl.",
                    "Heat olive oil in an oven-safe skillet over medium heat.",
                    "Sauté vegetables until softened.",
                    "Pour egg mixture over vegetables and cook for 5 minutes until edges start to set.",
                    "Sprinkle with cheese and transfer to oven.",
                    "Bake for 10-12 minutes until eggs are set and lightly golden.",
                    "Let cool slightly before slicing and serving."
                ]
            });
        }
        
        // Spinach recipe
        if (foodsLower.some(food => food.includes('spinach'))) {
            recipes.push({
                name: "Sautéed Garlic Spinach",
                ingredients: [
                    "1 lb fresh spinach",
                    "2 cloves garlic, minced",
                    "1 tbsp olive oil",
                    "Pinch of red pepper flakes (optional)",
                    "Salt and pepper to taste",
                    "Lemon juice (optional)"
                ],
                instructions: [
                    "Wash and dry spinach leaves thoroughly.",
                    "Heat olive oil in a large skillet over medium heat.",
                    "Add minced garlic and red pepper flakes (if using) and cook for 30 seconds until fragrant.",
                    "Add spinach in batches, stirring until wilted.",
                    "Season with salt and pepper.",
                    "Remove from heat and finish with a squeeze of lemon juice if desired.",
                    "Serve immediately."
                ]
            });
        }
        
        // Bacon recipe
        if (foodsLower.some(food => food.includes('bacon'))) {
            recipes.push({
                name: "Perfect Crispy Bacon",
                ingredients: [
                    "1/2 lb bacon slices",
                    "Optional: black pepper or brown sugar for seasoning"
                ],
                instructions: [
                    "Preheat oven to 400°F (200°C).",
                    "Line a baking sheet with parchment paper or aluminum foil.",
                    "Arrange bacon slices in a single layer without overlapping.",
                    "For extra flavor, sprinkle with black pepper or brown sugar if desired.",
                    "Bake for 15-20 minutes until desired crispness is reached.",
                    "Transfer to paper towels to drain excess grease.",
                    "Serve warm or use in other recipes."
                ]
            });
            
            // If we have both bacon and eggs, add a combo recipe
            if (foodsLower.some(food => food.includes('egg'))) {
                recipes.push({
                    name: "Bacon and Egg Breakfast Bowl",
                    ingredients: [
                        "4 slices bacon, cooked and crumbled",
                        "4 large eggs",
                        "1/4 cup shredded cheese",
                        "2 green onions, chopped",
                        "Salt and pepper to taste",
                        "Hot sauce (optional)"
                    ],
                    instructions: [
                        "Cook bacon until crispy, then crumble into pieces.",
                        "Scramble eggs in a bowl and season with salt and pepper.",
                        "Cook eggs in a non-stick pan over medium heat until just set.",
                        "Divide eggs between two bowls.",
                        "Top with crumbled bacon, shredded cheese, and green onions.",
                        "Add hot sauce if desired and serve immediately."
                    ]
                });
            }
        }
        
        // Broccoli recipe
        if (foodsLower.some(food => food.includes('broccoli'))) {
            recipes.push({
                name: "Roasted Broccoli with Garlic",
                ingredients: [
                    "1 lb broccoli florets",
                    "2-3 cloves garlic, minced",
                    "2 tbsp olive oil",
                    "1 tbsp lemon juice",
                    "Salt and pepper to taste",
                    "Grated Parmesan cheese (optional)"
                ],
                instructions: [
                    "Preheat oven to 425°F (220°C).",
                    "Toss broccoli florets with olive oil, garlic, salt and pepper on a baking sheet.",
                    "Spread in a single layer and roast for 15-20 minutes until edges are crispy.",
                    "Remove from oven and drizzle with lemon juice.",
                    "Sprinkle with Parmesan cheese if desired.",
                    "Serve hot as a side dish."
                ]
            });
        }
        
        // Sweet Potato recipes
        if (foodsLower.some(food => food.includes('sweet potato'))) {
            recipes.push({
                name: "Roasted Sweet Potato Cubes",
                ingredients: [
                    "2 large sweet potatoes, peeled and diced",
                    "2 tbsp olive oil",
                    "1 tsp paprika",
                    "1/2 tsp ground cumin",
                    "Salt and pepper to taste",
                    "Fresh herbs like rosemary or thyme (optional)"
                ],
                instructions: [
                    "Preheat oven to 425°F (220°C).",
                    "Toss sweet potato cubes with olive oil, paprika, cumin, salt, and pepper.",
                    "Spread in a single layer on a baking sheet.",
                    "Roast for 25-30 minutes, turning halfway through, until tender and caramelized.",
                    "Sprinkle with fresh herbs if using and serve hot."
                ]
            });

            // If we have eggs and sweet potato, add a breakfast hash recipe
            if (foodsLower.some(food => food.includes('egg'))) {
                recipes.push({
                    name: "Sweet Potato and Egg Breakfast Hash",
                    ingredients: [
                        "1 large sweet potato, diced small",
                        "1/2 onion, diced",
                        "1 bell pepper, diced (optional)",
                        "2 tbsp olive oil",
                        "2-4 eggs",
                        "1/2 tsp paprika",
                        "Salt and pepper to taste",
                        "Fresh herbs (parsley, chives, etc.)"
                    ],
                    instructions: [
                        "Heat olive oil in a large skillet over medium heat.",
                        "Add diced sweet potato and cook for 5-7 minutes until starting to soften.",
                        "Add onion and bell pepper, continue cooking for 5 minutes, stirring occasionally.",
                        "Season with paprika, salt, and pepper.",
                        "Create wells in the hash and crack eggs into them.",
                        "Cover and cook until eggs reach desired doneness (about 3-5 minutes).",
                        "Garnish with fresh herbs and serve immediately."
                    ]
                });
            }
        }
        
        // Apple recipes
        if (foodsLower.some(food => food.includes('apple'))) {
            recipes.push({
                name: "Healthy Apple Cinnamon Oatmeal",
                ingredients: [
                    "1 medium apple, diced",
                    "1 cup rolled oats",
                    "2 cups water or milk",
                    "1 tsp cinnamon",
                    "1 tbsp honey or maple syrup (optional)",
                    "Pinch of salt",
                    "Chopped nuts for garnish (optional)"
                ],
                instructions: [
                    "Combine oats, water/milk, and salt in a saucepan and bring to a boil.",
                    "Reduce heat and simmer for about 5 minutes.",
                    "Add diced apple and cinnamon, cook for another 2-3 minutes until apples soften slightly.",
                    "Remove from heat and sweeten with honey or maple syrup if desired.",
                    "Serve topped with additional apple slices and chopped nuts if using."
                ]
            });
            
            // If we have both apple and eggs
            if (foodsLower.some(food => food.includes('egg'))) {
                recipes.push({
                    name: "Apple-Cinnamon Dutch Baby (German Pancake)",
                    ingredients: [
                        "3 large eggs",
                        "1/2 cup flour",
                        "1/2 cup milk",
                        "1 tbsp sugar",
                        "1 tsp vanilla extract",
                        "Pinch of salt",
                        "2 tbsp butter",
                        "1 apple, thinly sliced",
                        "1/2 tsp cinnamon",
                        "Powdered sugar for dusting"
                    ],
                    instructions: [
                        "Preheat oven to 425°F (220°C) with a 10-inch cast iron skillet inside.",
                        "In a blender, combine eggs, flour, milk, sugar, vanilla, and salt. Blend until smooth.",
                        "Carefully remove hot skillet from oven, add butter and let it melt.",
                        "Arrange apple slices in the skillet and sprinkle with cinnamon.",
                        "Pour batter over the apples and immediately return to oven.",
                        "Bake for 20 minutes until puffed and golden brown.",
                        "Dust with powdered sugar and serve immediately while still puffed."
                    ]
                });
            }
        }

        // If we don't have specific recipes for these ingredients, add a generic one
        if (recipes.length === 0) {
            recipes.push({
                name: "Simple Mixed Bowl",
                ingredients: [
                    ...foods,
                    "Olive oil or butter",
                    "Your favorite seasonings (salt, pepper, herbs)",
                    "Optional: garlic, lemon juice, or vinegar for extra flavor"
                ],
                instructions: [
                    "Prepare all ingredients to appropriate sizes (chop vegetables, cook proteins if needed).",
                    "Heat oil or butter in a large pan over medium heat.",
                    "Add ingredients that take longest to cook first.",
                    "Season with your favorite spices and herbs.",
                    "Continue adding ingredients in order of cooking time.",
                    "Toss everything together until well combined and heated through.",
                    "Adjust seasoning to taste and serve hot."
                ]
            });
        }
        
        return recipes;
    }
    // Diet type selection functionality
    const dietTypeButtons = document.querySelectorAll('.diet-type-btn');
    const dietTypeInput = document.getElementById('diet_type');
    
    if (dietTypeButtons.length && dietTypeInput) {
        // Set initial active button based on form value
        const initialValue = dietTypeInput.value;
        dietTypeButtons.forEach(btn => {
            if (btn.getAttribute('data-value') === initialValue) {
                btn.classList.add('active');
            }
        });
        
        // Handle diet type button clicks
        dietTypeButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                dietTypeButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Set the hidden input value
                dietTypeInput.value = this.getAttribute('data-value');
            });
        });
    }
    
    // Meal count selection
    const mealCountSelect = document.getElementById('meal_count');
    const macroRecommendations = document.getElementById('macro-recommendations');
    
    // Update macro recommendations based on calorie input
    const calorieInput = document.getElementById('target_calories');
    if (calorieInput && macroRecommendations) {
        calorieInput.addEventListener('input', updateMacroRecommendations);
        
        // Initial update
        updateMacroRecommendations();
    }
    
    function updateMacroRecommendations() {
        if (!calorieInput) return;
        
        const calories = parseInt(calorieInput.value) || 2000;
        
        // Calculate recommended macros (approximation)
        const protein = Math.round(calories * 0.3 / 4); // 30% of calories from protein, 4 cal/g
        const carbs = Math.round(calories * 0.4 / 4);   // 40% of calories from carbs, 4 cal/g
        const fat = Math.round(calories * 0.3 / 9);     // 30% of calories from fat, 9 cal/g
        
        // Update the display
        const proteinElement = document.getElementById('recommended-protein');
        const carbsElement = document.getElementById('recommended-carbs');
        const fatElement = document.getElementById('recommended-fat');
        
        if (proteinElement && carbsElement && fatElement) {
            proteinElement.textContent = protein;
            carbsElement.textContent = carbs;
            fatElement.textContent = fat;
        }
    }
    
    // Show calorie calculator modal if user clicks the link
    const calorieCalculatorLink = document.getElementById('calorie-calculator-link');
    let calorieCalculatorModal;
    
    if (calorieCalculatorLink) {
        calorieCalculatorLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Create modal if it doesn't exist
            if (!calorieCalculatorModal) {
                const modalHtml = `
                    <div class="modal fade" id="calorieCalculatorModal" tabindex="-1" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">Calorie Calculator</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="mb-3">
                                        <label for="calc-gender" class="form-label">Gender</label>
                                        <select id="calc-gender" class="form-select">
                                            <option value="male">Male</option>
                                            <option value="female">Female</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label for="calc-age" class="form-label">Age</label>
                                        <input type="number" class="form-control" id="calc-age" min="15" max="100" value="30">
                                    </div>
                                    <div class="mb-3">
                                        <label for="calc-weight" class="form-label">Weight (kg)</label>
                                        <input type="number" class="form-control" id="calc-weight" min="30" max="300" value="70">
                                    </div>
                                    <div class="mb-3">
                                        <label for="calc-height" class="form-label">Height (cm)</label>
                                        <input type="number" class="form-control" id="calc-height" min="120" max="250" value="170">
                                    </div>
                                    <div class="mb-3">
                                        <label for="calc-activity" class="form-label">Activity Level</label>
                                        <select id="calc-activity" class="form-select">
                                            <option value="1.2">Sedentary (little or no exercise)</option>
                                            <option value="1.375">Lightly active (light exercise 1-3 days/week)</option>
                                            <option value="1.55" selected>Moderately active (moderate exercise 3-5 days/week)</option>
                                            <option value="1.725">Very active (hard exercise 6-7 days/week)</option>
                                            <option value="1.9">Extra active (very hard exercise & physical job)</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label for="calc-goal" class="form-label">Goal</label>
                                        <select id="calc-goal" class="form-select">
                                            <option value="lose">Lose weight</option>
                                            <option value="maintain" selected>Maintain weight</option>
                                            <option value="gain">Gain weight</option>
                                        </select>
                                    </div>
                                    <button id="calculate-btn" class="btn btn-primary w-100">Calculate</button>
                                    <div class="mt-3 p-3 border rounded d-none" id="calculation-result">
                                        <h5 class="mb-2">Recommended Daily Calories</h5>
                                        <div class="d-flex justify-content-between">
                                            <span>Maintenance:</span>
                                            <strong id="result-maintenance">0</strong>
                                        </div>
                                        <div class="d-flex justify-content-between">
                                            <span>For your goal:</span>
                                            <strong id="result-goal">0</strong>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                    <button type="button" class="btn btn-primary" id="use-calculated-value">Use This Value</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                calorieCalculatorModal = new bootstrap.Modal(document.getElementById('calorieCalculatorModal'));
                
                // Set up the calculator functionality
                const calculateBtn = document.getElementById('calculate-btn');
                calculateBtn.addEventListener('click', calculateCalories);
                
                // Set up the "Use This Value" button
                const useValueBtn = document.getElementById('use-calculated-value');
                useValueBtn.addEventListener('click', function() {
                    const goalCalories = document.getElementById('result-goal').textContent;
                    calorieInput.value = goalCalories;
                    updateMacroRecommendations();
                    calorieCalculatorModal.hide();
                });
            }
            
            calorieCalculatorModal.show();
        });
    }
    
    // Function to calculate calories based on user inputs
    function calculateCalories() {
        const gender = document.getElementById('calc-gender').value;
        const age = parseInt(document.getElementById('calc-age').value);
        const weight = parseFloat(document.getElementById('calc-weight').value);
        const height = parseFloat(document.getElementById('calc-height').value);
        const activity = parseFloat(document.getElementById('calc-activity').value);
        const goal = document.getElementById('calc-goal').value;
        
        // BMR calculation using Mifflin-St Jeor Equation
        let bmr;
        if (gender === 'male') {
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
        } else {
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
        }
        
        // Calculate maintenance calories
        const maintenanceCalories = Math.round(bmr * activity);
        
        // Calculate goal calories
        let goalCalories;
        switch (goal) {
            case 'lose':
                goalCalories = Math.round(maintenanceCalories * 0.8);
                break;
            case 'gain':
                goalCalories = Math.round(maintenanceCalories * 1.15);
                break;
            default:
                goalCalories = maintenanceCalories;
        }
        
        // Display results
        document.getElementById('result-maintenance').textContent = maintenanceCalories;
        document.getElementById('result-goal').textContent = goalCalories;
        document.getElementById('calculation-result').classList.remove('d-none');
    }
});
