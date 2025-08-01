// SchoolConnect API - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('SchoolConnect API loaded successfully');
    
    // Add any client-side functionality here
    const apiInfo = document.querySelector('.api-info');
    if (apiInfo) {
        apiInfo.addEventListener('click', function() {
            console.log('API info clicked');
        });
    }
    
    // Health check function
    function checkHealth() {
        fetch('/health/')
            .then(response => response.json())
            .then(data => {
                console.log('Health check:', data);
            })
            .catch(error => {
                console.error('Health check failed:', error);
            });
    }
    
    // Perform health check on load
    checkHealth();
}); 