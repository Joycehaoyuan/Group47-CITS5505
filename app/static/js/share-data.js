// Original jQuery code
$(document).ready(function() {
    // Username autocomplete functionality
    if ($("#recipient_username").length) {
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
    }
    
    // Listen for preview button click
    $(".preview-data-btn").on("click", function(e) {
        e.preventDefault();
        const dataId = $(this).data("id");
        const dataType = $(this).data("type");
        
        // Send AJAX request to get data details
        $.ajax({
            url: "/api/preview-data",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                data_id: dataId,
                data_type: dataType
            }),
            success: function(response) {
                if (response.success) {
                    // Display different content based on data type
                    if (dataType === "meal_plan") {
                        showMealPlanPreview(response.data);
                    } else if (dataType === "dietary_data") {
                        showDietaryDataPreview(response.data);
                    }
                    
                    // Show the preview modal
                    $("#dataPreviewModal").modal("show");
                } else {
                    alert("Failed to load preview: " + response.error);
                }
            },
            error: function() {
                alert("Error loading data preview");
            }
        });
    });

    // Display meal plan preview
    function showMealPlanPreview(data) {
        $("#previewModalTitle").text("Meal Plan Preview");
        
        let content = `
            <div class="card mb-3">
                <div class="card-header">
                    <strong>${data.name}</strong> - ${data.diet_type} Diet (${data.target_calories} calories)
                </div>
                <div class="card-body">
                    <div class="row">
        `;
        
        // Add each meal content
        data.meals.forEach(meal => {
            content += `
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-header">${meal.name}</div>
                        <div class="card-body">
                            <ul class="list-group">
            `;
            
            meal.foods.forEach(food => {
                content += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        ${food.name}
                        <span class="badge bg-primary rounded-pill">${food.calories} cal</span>
                    </li>
                `;
            });
            
            content += `
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        });
        
        content += `
                    </div>
                </div>
                <div class="card-footer text-muted">
                    Created on ${new Date(data.date_created).toLocaleDateString()}
                </div>
            </div>
        `;
        
        $("#previewModalBody").html(content);
    }
    
    // Display dietary data preview
    function showDietaryDataPreview(data) {
        $("#previewModalTitle").text("Dietary Data Preview");
        
        const date = new Date(data.date).toLocaleDateString();
        
        let content = `
            <div class="card">
                <div class="card-header">
                    <strong>Dietary Data for ${date}</strong>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h5 class="card-title">Calories</h5>
                                    <p class="card-text">${data.calories}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h5 class="card-title">Protein</h5>
                                    <p class="card-text">${data.protein}g</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h5 class="card-title">Carbs</h5>
                                    <p class="card-text">${data.carbs}g</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h5 class="card-title">Fat</h5>
                                    <p class="card-text">${data.fat}g</p>
                                </div>
                            </div>
                        </div>
                    </div>
        `;
        
        // Display meal information (if available)
        if (data.meals && data.meals.length > 0) {
            content += `<h5 class="mt-4">Meals</h5>`;
            
            data.meals.forEach((meal, idx) => {
                content += `
                    <div class="card mb-2">
                        <div class="card-header">Meal ${idx + 1}</div>
                        <div class="card-body">
                            <p><strong>Name:</strong> ${meal.name || 'Not specified'}</p>
                            <p><strong>Foods:</strong> ${meal.foods ? meal.foods.join(', ') : 'None recorded'}</p>
                        </div>
                    </div>
                `;
            });
        }
        
        // Display notes (if available)
        if (data.notes) {
            content += `
                <h5 class="mt-4">Notes</h5>
                <div class="card">
                    <div class="card-body">
                        ${data.notes}
                    </div>
                </div>
            `;
        }
        
        content += `
                </div>
                <div class="card-footer text-muted">
                    Recorded on ${new Date(data.upload_date).toLocaleDateString()}
                </div>
            </div>
        `;
        
        $("#previewModalBody").html(content);
    }
});

// Code originally embedded in HTML
document.addEventListener('DOMContentLoaded', function() {
    // Get elements to manipulate
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
    
    // Initialize page data
    // Note: These data are generated through Jinja2 templates in HTML, we can only add code structure here
    // Actual data will be provided through JavaScript variable declarations in the HTML template
    // So this part of the code needs to keep these variable declarations in the HTML template
    
    // Toggle selectors based on data type
    function updateDataSelectionVisibility() {
        const selectedType = dataTypeSelect.value;
        
        if (selectedType === 'meal_plan') {
            mealPlanContainer.style.display = 'block';
            dietaryDataContainer.style.display = 'none';
            mealPlanPreviewCard.style.display = 'block';
            dietaryDataPreviewCard.style.display = 'none';
            
            if (mealPlanSelect.options.length > 0) {
                dataIdInput.value = mealPlanSelect.value;
                updateMealPlanPreview(mealPlanSelect.value);
            }
        } else {
            mealPlanContainer.style.display = 'none';
            dietaryDataContainer.style.display = 'block';
            mealPlanPreviewCard.style.display = 'none';
            dietaryDataPreviewCard.style.display = 'block';
            
            if (dietaryDataSelect.options.length > 0) {
                dataIdInput.value = dietaryDataSelect.value;
                updateDietaryDataPreview(dietaryDataSelect.value);
            }
        }
    }
    
    // Update meal plan preview
    function updateMealPlanPreview(planId) {
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
        
        html += '</div>';
        mealPlanPreview.innerHTML = html;
    }
    
    // Update dietary data preview
    function updateDietaryDataPreview(dataId) {
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
    
    // Initialize form state
    updateDataSelectionVisibility();
    
    // Add event listeners
    dataTypeSelect.addEventListener('change', updateDataSelectionVisibility);
    
    mealPlanSelect.addEventListener('change', function() {
        dataIdInput.value = this.value;
        updateMealPlanPreview(this.value);
    });
    
    dietaryDataSelect.addEventListener('change', function() {
        dataIdInput.value = this.value;
        updateDietaryDataPreview(this.value);
    });
});