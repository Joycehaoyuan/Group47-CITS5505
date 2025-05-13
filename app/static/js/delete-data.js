// static/js/delete-data.js
document.addEventListener('DOMContentLoaded', function() {
    // add event listeners to all delete buttons
    document.querySelectorAll('.delete-data').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const dataId = this.getAttribute('data-id');
            const tableRow = this.closest('tr');
            const dateText = tableRow.querySelector('td:first-child').textContent;
            
            if (confirm(`Are you sure to delete ${dateText} data? This action cannot be undone.`)) {
                // get CSRF token from the meta tag
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                
                // AJAX request to delete the data
                fetch(`/delete-dietary-data/${dataId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (response.ok) {
                        // remove the table row
                        tableRow.style.backgroundColor = '#ffe2e2';
                        tableRow.style.transition = 'background-color 0.5s ease, opacity 0.5s ease';
                        
                        setTimeout(() => {
                            tableRow.style.opacity = '0';
                            setTimeout(() => {
                                tableRow.remove();
                                showFlashMessage('营养数据已成功删除。', 'success');
                                
                                // If no rows are left in the table, show a message
                                const remainingRows = document.querySelectorAll('tbody tr').length;
                                if (remainingRows === 0) {
                                    const tableBody = document.querySelector('tbody');
                                    const noDataRow = document.createElement('tr');
                                    noDataRow.innerHTML = '<td colspan="7" class="text-center">暂无营养数据记录</td>';
                                    tableBody.appendChild(noDataRow);
                                }
                            }, 500);
                        }, 300);
                    } else {
                        showFlashMessage('删除数据时出错。', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showFlashMessage('删除数据时发生错误。', 'danger');
                });
            }
        });
    });
    
    // Function to show flash messages
    function showFlashMessage(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Automatically remove the alert after 3 seconds
        setTimeout(() => {
            alertDiv.style.opacity = '0';
            setTimeout(() => alertDiv.remove(), 500);
        }, 3000);
    }
});