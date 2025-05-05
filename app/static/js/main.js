// Main JavaScript for meal planner application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle meal refresh buttons
    const refreshButtons = document.querySelectorAll('.refresh-meal-btn');
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
                },
                body: JSON.stringify({
                    meal_plan_id: mealPlanId,
                    meal_index: mealIndex
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the meal in the UI
                    updateMealDisplay(mealIndex, data.meal);
                } else {
                    alert('Error: ' + data.error);
                }
                
                // Restore button
                this.innerHTML = '<i class="fas fa-sync-alt"></i>';
                this.disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while refreshing the meal.');
                
                // Restore button
                this.innerHTML = '<i class="fas fa-sync-alt"></i>';
                this.disabled = false;
            });
        });
    });
    
    // Data sharing functionality
    const shareDataTypeSelect = document.getElementById('data_type');
    const mealPlanSelect = document.getElementById('meal_plan_select');
    const dietaryDataSelect = document.getElementById('dietary_data_select');
    const dataIdInput = document.getElementById('data_id');
    
    if (shareDataTypeSelect && mealPlanSelect && dietaryDataSelect && dataIdInput) {
        // Initial setup
        updateDataSelectionVisibility();
        
        // When data type changes, update the visible select
        shareDataTypeSelect.addEventListener('change', function() {
            updateDataSelectionVisibility();
        });
        
        // When meal plan is selected, update the data ID
        mealPlanSelect.addEventListener('change', function() {
            dataIdInput.value = this.value;
        });
        
        // When dietary data is selected, update the data ID
        dietaryDataSelect.addEventListener('change', function() {
            dataIdInput.value = this.value;
        });
        
        function updateDataSelectionVisibility() {
            if (shareDataTypeSelect && mealPlanSelect && dietaryDataSelect && dataIdInput) {
                if (shareDataTypeSelect.value === 'meal_plan') {
                    if (mealPlanSelect.parentElement) mealPlanSelect.parentElement.style.display = 'block';
                    if (dietaryDataSelect.parentElement) dietaryDataSelect.parentElement.style.display = 'none';
                    dataIdInput.value = mealPlanSelect.value;
                } else {
                    if (mealPlanSelect.parentElement) mealPlanSelect.parentElement.style.display = 'none';
                    if (dietaryDataSelect.parentElement) dietaryDataSelect.parentElement.style.display = 'block';
                    dataIdInput.value = dietaryDataSelect.value;
                }
            }
        }
    }
    
    // Function to update meal display after refresh
    function updateMealDisplay(mealIndex, mealData) {
        const mealContainer = document.querySelector(`.meal-container[data-meal-index="${mealIndex}"]`);
        if (!mealContainer) return;
        
        // Update meal title and total calories
        const mealHeader = mealContainer.querySelector('.meal-header');
        if (mealHeader) {
            mealHeader.innerHTML = `
                <h4>${mealData.name} <small class="text-muted">${mealData.total_calories} calories</small></h4>
                <div class="nutrient-pills">
                    <span class="badge bg-primary">Protein: ${mealData.total_protein}g</span>
                    <span class="badge bg-success">Carbs: ${mealData.total_carbs}g</span>
                    <span class="badge bg-warning">Fat: ${mealData.total_fat}g</span>
                </div>
            `;
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
    }
    
    // Handle manual data entry form in upload_data.html
    const mealFormContainer = document.getElementById('meal-form-container');
    const addMealButton = document.getElementById('add-meal-btn');
    const mealsJsonInput = document.getElementById('meals_json');
    
    if (mealFormContainer && addMealButton && mealsJsonInput) {
        let meals = [];
        let mealCounter = 0;
        
        // Add a new meal form
        addMealButton.addEventListener('click', function() {
            const mealId = mealCounter++;
            const mealHtml = `
                <div class="card mb-3 meal-entry" data-meal-id="${mealId}">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <input type="text" class="form-control form-control-sm meal-name" placeholder="Meal name" style="width: 200px;" value="Meal ${mealId + 1}">
                        <button type="button" class="btn btn-sm btn-danger remove-meal" data-meal-id="${mealId}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="food-entries">
                            <div class="row mb-2 food-entry">
                                <div class="col-5">
                                    <input type="text" class="form-control food-name" placeholder="Food name">
                                </div>
                                <div class="col-3">
                                    <input type="text" class="form-control food-serving" placeholder="Serving">
                                </div>
                                <div class="col-2">
                                    <input type="number" class="form-control food-calories" placeholder="Calories" min="0">
                                </div>
                                <div class="col-2">
                                    <button type="button" class="btn btn-sm btn-outline-danger remove-food">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-primary add-food" data-meal-id="${mealId}">
                            <i class="fas fa-plus"></i> Add Food
                        </button>
                    </div>
                </div>
            `;
            
            mealFormContainer.insertAdjacentHTML('beforeend', mealHtml);
            meals.push({
                id: mealId,
                name: `Meal ${mealId + 1}`,
                foods: []
            });
            updateMealsJson();
        });
        
        // Event delegation for dynamically added elements
        mealFormContainer.addEventListener('click', function(e) {
            // Remove a meal
            if (e.target.classList.contains('remove-meal') || e.target.closest('.remove-meal')) {
                const button = e.target.classList.contains('remove-meal') ? e.target : e.target.closest('.remove-meal');
                const mealId = parseInt(button.getAttribute('data-meal-id'));
                const mealElement = document.querySelector(`.meal-entry[data-meal-id="${mealId}"]`);
                
                if (mealElement) {
                    mealElement.remove();
                    meals = meals.filter(meal => meal.id !== mealId);
                    updateMealsJson();
                }
            }
            
            // Add a food to a meal
            if (e.target.classList.contains('add-food') || e.target.closest('.add-food')) {
                const button = e.target.classList.contains('add-food') ? e.target : e.target.closest('.add-food');
                const mealId = parseInt(button.getAttribute('data-meal-id'));
                const foodEntriesContainer = button.closest('.card-body').querySelector('.food-entries');
                
                if (foodEntriesContainer) {
                    const foodHtml = `
                        <div class="row mb-2 food-entry">
                            <div class="col-5">
                                <input type="text" class="form-control food-name" placeholder="Food name">
                            </div>
                            <div class="col-3">
                                <input type="text" class="form-control food-serving" placeholder="Serving">
                            </div>
                            <div class="col-2">
                                <input type="number" class="form-control food-calories" placeholder="Calories" min="0">
                            </div>
                            <div class="col-2">
                                <button type="button" class="btn btn-sm btn-outline-danger remove-food">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        </div>
                    `;
                    
                    foodEntriesContainer.insertAdjacentHTML('beforeend', foodHtml);
                }
            }
            
            // Remove a food
            if (e.target.classList.contains('remove-food') || e.target.closest('.remove-food')) {
                const button = e.target.classList.contains('remove-food') ? e.target : e.target.closest('.remove-food');
                const foodEntry = button.closest('.food-entry');
                
                if (foodEntry) {
                    foodEntry.remove();
                    updateMealsFromForm();
                }
            }
        });
        
        // Update meals when input changes
        mealFormContainer.addEventListener('input', function(e) {
            if (e.target.classList.contains('meal-name') || 
                e.target.classList.contains('food-name') || 
                e.target.classList.contains('food-serving') || 
                e.target.classList.contains('food-calories')) {
                
                updateMealsFromForm();
            }
        });
        
        // Update the hidden input with the meals JSON data
        function updateMealsJson() {
            mealsJsonInput.value = JSON.stringify(meals);
        }
        
        // Read the form and update the meals array
        function updateMealsFromForm() {
            const mealElements = document.querySelectorAll('.meal-entry');
            const updatedMeals = [];
            
            mealElements.forEach(mealElement => {
                const mealId = parseInt(mealElement.getAttribute('data-meal-id'));
                const mealName = mealElement.querySelector('.meal-name').value;
                const foodEntries = mealElement.querySelectorAll('.food-entry');
                const foods = [];
                
                foodEntries.forEach(foodEntry => {
                    const foodName = foodEntry.querySelector('.food-name').value;
                    const foodServing = foodEntry.querySelector('.food-serving').value;
                    const foodCalories = foodEntry.querySelector('.food-calories').value;
                    
                    if (foodName.trim() !== '') {
                        foods.push({
                            name: foodName,
                            serving: foodServing,
                            calories: parseInt(foodCalories) || 0
                        });
                    }
                });
                
                updatedMeals.push({
                    id: mealId,
                    name: mealName,
                    foods: foods
                });
            });
            
            meals = updatedMeals;
            updateMealsJson();
        }
    }
});
