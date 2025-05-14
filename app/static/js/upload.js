document.addEventListener('DOMContentLoaded', function() {
    // Initialize date field with today's date, but allow changing to any date
    const dateField = document.getElementById('date');
    if (dateField && !dateField.value) {
        const today = new Date();
        const year = today.getFullYear();
        let month = today.getMonth() + 1;
        let day = today.getDate();
        
        month = month < 10 ? '0' + month : month;
        day = day < 10 ? '0' + day : day;
        
        dateField.value = `${year}-${month}-${day}`;
        
        // Remove min and max attributes to allow any date
        dateField.removeAttribute('min');
        dateField.removeAttribute('max');
    }
    
    // Calorie Calculator functionality
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
                                        <div class="mt-2 small text-muted">
                                            <p class="mb-1">When you use this value, we'll automatically calculate:</p>
                                            <ul class="mb-0">
                                                <li>Protein: 30% of calories (4 cal/g)</li>
                                                <li>Carbs: 45% of calories (4 cal/g)</li>
                                                <li>Fat: 25% of calories (9 cal/g)</li>
                                            </ul>
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
                    const goalCalories = parseInt(document.getElementById('result-goal').textContent);
                    
                    // Get all form inputs
                    const calorieInput = document.getElementById('calories');
                    const proteinInput = document.getElementById('protein');
                    const carbsInput = document.getElementById('carbs');
                    const fatInput = document.getElementById('fat');
                    
                    // Set calorie value
                    if (calorieInput) {
                        calorieInput.value = goalCalories;
                    }
                    
                    // Set macronutrient values based on calorie value
                    if (proteinInput) {
                        const protein = Math.round(goalCalories * 0.30 / 4);
                        proteinInput.value = protein;
                    }
                    
                    if (carbsInput) {
                        const carbs = Math.round(goalCalories * 0.45 / 4);
                        carbsInput.value = carbs;
                    }
                    
                    if (fatInput) {
                        const fat = Math.round(goalCalories * 0.25 / 9);
                        fatInput.value = fat;
                    }
                    
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
    
    // Add more upload page functionality here as needed
});