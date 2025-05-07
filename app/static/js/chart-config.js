// Chart configuration for nutrition data visualization

function initializeCharts(chartData) {
    // Parse the chart data (it will be passed as a string from Flask)
    const data = typeof chartData === 'string' ? JSON.parse(chartData) : chartData;
    
    // If no data, don't initialize charts
    if (!data || !data.dates || data.dates.length === 0) {
        document.getElementById('no-data-message').style.display = 'block';
        document.getElementById('charts-container').style.display = 'none';
        return;
    }
    
    document.getElementById('no-data-message').style.display = 'none';
    document.getElementById('charts-container').style.display = 'block';
    
    // Initialize calories chart
    const caloriesCtx = document.getElementById('calories-chart').getContext('2d');
    const caloriesChart = new Chart(caloriesCtx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Daily Calories',
                data: data.calories,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 3,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Calories: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Calories'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
    
    // Initialize macronutrients chart
    const macroCtx = document.getElementById('macro-chart').getContext('2d');
    const macroChart = new Chart(macroCtx, {
        type: 'bar',
        data: {
            labels: data.dates,
            datasets: [
                {
                    label: 'Protein (g)',
                    data: data.protein,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Carbs (g)',
                    data: data.carbs,
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Fat (g)',
                    data: data.fat,
                    backgroundColor: 'rgba(255, 159, 64, 0.5)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}g`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Grams'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
    
    // Initialize average macronutrient distribution pie chart
    if (data.protein.length > 0) {
        // Calculate averages
        const avgProtein = data.protein.reduce((a, b) => a + b, 0) / data.protein.length;
        const avgCarbs = data.carbs.reduce((a, b) => a + b, 0) / data.carbs.length;
        const avgFat = data.fat.reduce((a, b) => a + b, 0) / data.fat.length;
        
        const macroDistributionCtx = document.getElementById('macro-distribution-chart').getContext('2d');
        const macroDistributionChart = new Chart(macroDistributionCtx, {
            type: 'pie',
            data: {
                labels: ['Protein', 'Carbs', 'Fat'],
                datasets: [{
                    data: [avgProtein, avgCarbs, avgFat],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(255, 159, 64, 0.7)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value.toFixed(1)}g (${percentage}%)`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Average Macronutrient Distribution'
                    }
                }
            }
        });
    }
}

// Call this function when the document is ready and chart data is available
document.addEventListener('DOMContentLoaded', function() {
    const chartDataElement = document.getElementById('chart-data');
    if (chartDataElement) {
        const chartData = chartDataElement.getAttribute('data-chart');
        initializeCharts(chartData);
    }
});
