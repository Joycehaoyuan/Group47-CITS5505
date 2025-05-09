// Meal Plan generation and management functionality

document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Handle meal refresh buttons
    const refreshButtons = document.querySelectorAll('.refresh-meal-btn');
    if (refreshButtons.length > 0) {
        refreshButtons.forEach(button => {
            button.addEventListener('click', function() {
                const mealPlanId = this.getAttribute('data-meal-plan-id');
                const mealIndex = this.getAttribute('data-meal-index');
                
                // Show loading spinner
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
                this.disabled = true;
                
                // Send AJAX request to refresh meal
                fetch('/api/refresh-meal', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        meal_plan_id: mealPlanId,
                        meal_index: mealIndex
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // Update the meal in the UI
                        updateMealDisplay(mealIndex, data.meal);
                    } else {
                        alert('Error: ' + (data.error || 'Failed to refresh meal'));
                    }
                    
                    // Restore button
                    this.innerHTML = '<i class="fas fa-sync-alt"></i>';
                    this.disabled = false;
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while refreshing the meal. Please try again.');
                    
                    // Restore button
                    this.innerHTML = '<i class="fas fa-sync-alt"></i>';
                    this.disabled = false;
                });
            });
        });
    }
    
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
                                    <div id="recipe-error" class="alert alert-danger mt-3" style="display:none;"></div>
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
        const recipeError = document.getElementById('recipe-error');
        if (recipesLoading) recipesLoading.style.display = 'block';
        if (recipeContent) recipeContent.style.display = 'none';
        if (recipeError) recipeError.style.display = 'none';
        
        // Show the modal
        const modal = new bootstrap.Modal(recipeSuggestionsModal);
        modal.show();
        
        // Default recipes in case API fails
        const defaultRecipes = [
            {
                name: "Whole Grain Breakfast Bowl",
                ingredients: [
                    "1 cup cooked brown rice",
                    "1/2 cup strawberries, sliced",
                    "1 slice whole wheat bread, toasted and diced",
                    "1 tbsp honey or maple syrup",
                    "1/4 cup yogurt",
                    "1 tbsp nuts or seeds"
                ],
                instructions: [
                    "Combine cooked brown rice and diced whole wheat toast in a bowl",
                    "Top with sliced strawberries",
                    "Drizzle with honey or maple syrup",
                    "Add a dollop of yogurt on top",
                    "Sprinkle with nuts or seeds for extra crunch and protein"
                ]
            },
            {
                name: "Strawberry Paleo Breakfast Bowl",
                ingredients: [
                    "1 paleo breakfast bowl base",
                    "1 cup fresh strawberries, sliced",
                    "1/4 cup almond milk",
                    "1 tbsp almond butter",
                    "1 tsp cinnamon",
                    "1 tbsp honey (optional)"
                ],
                instructions: [
                    "Place paleo breakfast bowl base in a bowl",
                    "Add sliced strawberries on top",
                    "Pour almond milk over the mixture",
                    "Drizzle with almond butter and honey if using",
                    "Sprinkle with cinnamon and serve immediately"
                ]
            }
        ];
        
        // Get recipe suggestions from API
        fetch('/api/recipe-suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                foods: foods,
                meal_name: mealName
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading and show content
            if (recipesLoading) recipesLoading.style.display = 'none';
            if (recipeContent) recipeContent.style.display = 'block';
            
            // Generate recipe suggestions
            const recipeList = document.getElementById('recipe-list');
            recipeList.innerHTML = '';
            
            if (data.success && data.recipes && data.recipes.length > 0) {
                data.recipes.forEach(recipe => {
                    const recipeCard = createRecipeCard(recipe);
                    recipeList.appendChild(recipeCard);
                });
            } else {
                // If API doesn't return recipes, use default recipes
                defaultRecipes.forEach(recipe => {
                    const recipeCard = createRecipeCard(recipe);
                    recipeList.appendChild(recipeCard);
                });
            }
        })
        .catch(error => {
            console.error('Error getting recipe suggestions:', error);
            
            // Hide loading and show content with default recipes
            if (recipesLoading) recipesLoading.style.display = 'none';
            if (recipeContent) recipeContent.style.display = 'block';
            
            const recipeList = document.getElementById('recipe-list');
            recipeList.innerHTML = '';
            
            // Display default recipes
            defaultRecipes.forEach(recipe => {
                const recipeCard = createRecipeCard(recipe);
                recipeList.appendChild(recipeCard);
            });
        });
    }
    
    // Function to create recipe card
    function createRecipeCard(recipe) {
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
        
        return recipeCard;
    }
    
    // Function to update meal display after refresh
    function updateMealDisplay(mealIndex, mealData) {
        const mealContainer = document.querySelector(`.meal-container[data-meal-index="${mealIndex}"]`);
        if (!mealContainer) return;
        
        // Update meal title and total calories
        const mealHeader = mealContainer.querySelector('.meal-header');
        if (mealHeader) {
            const nutrientHtml = `
                <div>
                    <h4>${mealData.name} <small class="text-muted">${mealData.total_calories} calories</small></h4>
                    <div class="nutrient-pills">
                        <span class="badge bg-primary">Protein: ${mealData.total_protein}g</span>
                        <span class="badge bg-primary">Carbs: ${mealData.total_carbs}g</span>
                        <span class="badge bg-primary">Fat: ${mealData.total_fat}g</span>
                    </div>
                </div>
            `;
            
            // Keep the refresh button
            const refreshButton = mealHeader.querySelector('.refresh-meal-btn');
            mealHeader.innerHTML = nutrientHtml;
            
            // Re-add the refresh button if it exists
            if (refreshButton) {
                mealHeader.appendChild(refreshButton);
            }
        }
        
        // Update food items
        const foodList = mealContainer.querySelector('.list-group');
        if (foodList) {
            let foodItems = '';
            mealData.foods.forEach(food => {
                foodItems += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${food.name}</strong>
                            <small class="d-block text-muted">${food.serving}</small>
                        </div>
                        <span class="badge bg-light text-dark rounded-pill">${food.calories} cal</span>
                    </li>
                `;
            });
            foodList.innerHTML = foodItems;
        }
        
        // Update recipe suggestions button
        const recipeBtn = mealContainer.querySelector('.recipe-suggestion-btn');
        if (recipeBtn) {
            const foodsData = mealData.foods.map(food => food.name).join(',');
            recipeBtn.setAttribute('data-foods', foodsData);
        }
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