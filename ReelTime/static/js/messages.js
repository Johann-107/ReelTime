// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            alert.classList.add('fade-out');
            
            // Remove from DOM after animation completes
            setTimeout(function() {
                alert.remove();
            }, 300); // Match animation duration
        }, 5000); // Show for 5 seconds
    });
});
