// JavaScript for share data functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get the elements to operate on
    const dataTypeSelect = document.getElementById('data_type');
    const mealPlanContainer = document.getElementById('meal_plan_select_container');
    const dietaryDataContainer = document.getElementById('dietary_data_select_container');
    const mealPlanSelect = document.getElementById('meal_plan_select');
    const dietaryDataSelect = document.getElementById('dietary_data_select');
    const dataIdInput = document.getElementById('data_id');
    const mealPlanPreviewCard = document.getElementById('meal_plan_preview_card');
    const dietaryDataPreviewCard = document.getElementById('dietary_data_preview_card');
    const mealPlanPreview = document.getElementById('meal_plan_preview');
    const dietaryDataPreview = document.getElementById('dietary_data_preview');
    
    // Switch selector based on data type
    function updateDataSelectionVisibility() {
        if (!dataTypeSelect || !mealPlanContainer || !dietaryDataContainer) return;
        
        const selectedType = dataTypeSelect.value;
        
        if (selectedType === 'meal_plan') {
            mealPlanContainer.style.display = 'block';
            dietaryDataContainer.style.display = 'none';
            if (mealPlanPreviewCard) mealPlanPreviewCard.style.display = 'block';
            if (dietaryDataPreviewCard) dietaryDataPreviewCard.style.display = 'none';
            
            if (mealPlanSelect && mealPlanSelect.options.length > 0 && dataIdInput) {
                dataIdInput.value = mealPlanSelect.value;
                updateMealPlanPreview(mealPlanSelect.value);
            }
        } else {
            mealPlanContainer.style.display = 'none';
            dietaryDataContainer.style.display = 'block';
            if (mealPlanPreviewCard) mealPlanPreviewCard.style.display = 'none';
            if (dietaryDataPreviewCard) dietaryDataPreviewCard.style.display = 'block';
            
            if (dietaryDataSelect && dietaryDataSelect.options.length > 0 && dataIdInput) {
                dataIdInput.value = dietaryDataSelect.value;
                updateDietaryDataPreview(dietaryDataSelect.value);
            }
        }
    }
    
    // Update meal plan preview
    function updateMealPlanPreview(planId) {
        if (!mealPlanPreview) return;
        
        const plan = window.mealPlans ? window.mealPlans[planId] : null;
        if (!plan) {
            mealPlanPreview.innerHTML = '<div class="alert alert-warning">Unable to load meal plan preview</div>';
            return;
        }
        
        let html = `
            <div class="mb-3">
                <div class="row">
                    <div class="col-md-4">
                        <p class="mb-1"><strong>Diet Type:</strong> ${plan.dietType}</p>
                    </div>
                    <div class="col-md-4">
                        <p class="mb-1"><strong>Target Calories:</strong> ${plan.targetCalories}</p>
                    </div>
                    <div class="col-md-4">
                        <p class="mb-1"><strong>Meal Count:</strong> ${plan.mealCount}</p>
                    </div>
                </div>
            </div>
            
            <h5 class="mb-3">Meals</h5>
            <div class="row">
        `;
        
        // Add each meal content
        if (plan.meals && Array.isArray(plan.meals)) {
            for (const meal of plan.meals) {
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card bg-light">
                            <div class="card-header">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h5 class="mb-0">${meal.name}</h5>
                                    <span class="badge bg-primary">${meal.total_calories} calories</span>
                                </div>
                            </div>
                            <ul class="list-group list-group-flush">
                `;
                
                // Add each food
                if (meal.foods && Array.isArray(meal.foods)) {
                    for (const food of meal.foods) {
                        html += `
                            <li class="list-group-item">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>${food.name}</strong>
                                        <small class="d-block text-muted">${food.serving}</small>
                                    </div>
                                    <span class="badge bg-secondary">${food.calories} calories</span>
                                </div>
                            </li>
                        `;
                    }
                }
                
                html += `
                            </ul>
                            <div class="card-footer text-center">
                                <div class="d-flex justify-content-between">
                                    <span class="badge bg-primary">Protein: ${meal.total_protein}g</span>
                                    <span class="badge bg-success">Carbs: ${meal.total_carbs}g</span>
                                    <span class="badge bg-warning text-dark">Fat: ${meal.total_fat}g</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        }
        
        html += '</div>';
        mealPlanPreview.innerHTML = html;
    }
    
    // Update dietary data preview
    function updateDietaryDataPreview(dataId) {
        if (!dietaryDataPreview) return;
        
        const data = window.dietaryData ? window.dietaryData[dataId] : null;
        if (!data) {
            dietaryDataPreview.innerHTML = '<div class="alert alert-warning">Unable to load dietary data preview</div>';
            return;
        }
        
        let html = `
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="card bg-light text-center p-3">
                        <h3>${data.calories}</h3>
                        <p class="mb-0">Calories</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light text-center p-3">
                        <h3>${data.protein}g</h3>
                        <p class="mb-0">Protein</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light text-center p-3">
                        <h3>${data.carbs}g</h3>
                        <p class="mb-0">Carbs</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light text-center p-3">
                        <h3>${data.fat}g</h3>
                        <p class="mb-0">Fat</p>
                    </div>
                </div>
            </div>
        `;
        
        if (data.notes && data.notes.trim() !== '') {
            html += `
                <div class="alert alert-info">
                    <h5 class="alert-heading">Notes</h5>
                    <p class="mb-0">${data.notes}</p>
                </div>
            `;
        }
        
        dietaryDataPreview.innerHTML = html;
    }
    
    // Initialize everything if elements exist
    if (dataTypeSelect) {
        // Initialize form state
        updateDataSelectionVisibility();
        
        // Add event listeners
        dataTypeSelect.addEventListener('change', updateDataSelectionVisibility);
        
        if (mealPlanSelect) {
            mealPlanSelect.addEventListener('change', function() {
                if (dataIdInput) dataIdInput.value = this.value;
                updateMealPlanPreview(this.value);
            });
        }
        
        if (dietaryDataSelect) {
            dietaryDataSelect.addEventListener('change', function() {
                if (dataIdInput) dataIdInput.value = this.value;
                updateDietaryDataPreview(this.value);
            });
        }
        
        // Initialize data ID input with initial selection
        if (dataIdInput) {
            if (mealPlanSelect && mealPlanSelect.options.length > 0 && dataTypeSelect.value === 'meal_plan') {
                dataIdInput.value = mealPlanSelect.value;
            } else if (dietaryDataSelect && dietaryDataSelect.options.length > 0 && dataTypeSelect.value === 'dietary_data') {
                dataIdInput.value = dietaryDataSelect.value;
            }
        }
    }
    
    // Username autocomplete with optional jQuery UI
    if (typeof $ !== 'undefined' && $.fn.autocomplete && $("#recipient_username").length) {
        try {
            $("#recipient_username").autocomplete({
                source: function(request, response) {
                    $.ajax({
                        url: "/api/users",
                        dataType: "json",
                        data: {
                            term: request.term
                        },
                        success: function(data) {
                            response(data.users);
                        }
                    });
                },
                minLength: 2
            });
        } catch (e) {
            console.error("Error initializing autocomplete:", e);
        }
    }
    
    // Enable bootstrap tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        try {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.forEach(function (tooltipTriggerEl) {
                new bootstrap.Tooltip(tooltipTriggerEl);
            });
        } catch (e) {
            console.error("Error initializing tooltips:", e);
        }
    }
});