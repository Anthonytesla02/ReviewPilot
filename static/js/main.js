// Main JavaScript file for Review Automation Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize auto-hiding alerts
    initializeAlerts();
    
    // Initialize form enhancements
    initializeFormEnhancements();
    
    // Initialize rating interactions
    initializeRatingStars();
    
    // Initialize data tables
    initializeDataTables();
    
    // Initialize dashboard updates
    initializeDashboard();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Auto-hide alerts after 5 seconds
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        // Only auto-hide success and info alerts
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

/**
 * Form enhancements and validation
 */
function initializeFormEnhancements() {
    // Add loading state to form buttons
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !form.classList.contains('no-loading')) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Please wait...';
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        autoResize(textarea);
        textarea.addEventListener('input', function() {
            autoResize(this);
        });
    });
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
}

/**
 * Auto-resize textarea based on content
 */
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

/**
 * Email validation with visual feedback
 */
function validateEmail(input) {
    const email = input.value;
    const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    const feedback = input.parentNode.querySelector('.email-feedback');
    
    if (email && !isValid) {
        input.classList.add('is-invalid');
        if (!feedback) {
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'invalid-feedback email-feedback';
            feedbackDiv.textContent = 'Please enter a valid email address';
            input.parentNode.appendChild(feedbackDiv);
        }
    } else {
        input.classList.remove('is-invalid');
        if (feedback) {
            feedback.remove();
        }
    }
}

/**
 * Initialize interactive rating stars
 */
function initializeRatingStars() {
    const ratingContainers = document.querySelectorAll('.rating-interactive');
    ratingContainers.forEach(function(container) {
        const stars = container.querySelectorAll('.fa-star');
        const input = container.querySelector('input[type="hidden"]');
        
        stars.forEach(function(star, index) {
            star.addEventListener('click', function() {
                const rating = index + 1;
                if (input) input.value = rating;
                
                // Update visual stars
                stars.forEach(function(s, i) {
                    if (i < rating) {
                        s.classList.remove('text-muted');
                        s.classList.add('text-warning');
                    } else {
                        s.classList.remove('text-warning');
                        s.classList.add('text-muted');
                    }
                });
                
                // Trigger change event
                if (input) {
                    const event = new Event('change');
                    input.dispatchEvent(event);
                }
            });
            
            // Hover effects
            star.addEventListener('mouseenter', function() {
                const hoverRating = index + 1;
                stars.forEach(function(s, i) {
                    if (i < hoverRating) {
                        s.style.color = '#ffc107';
                    } else {
                        s.style.color = '';
                    }
                });
            });
        });
        
        // Reset on mouse leave
        container.addEventListener('mouseleave', function() {
            const currentRating = input ? parseInt(input.value) || 0 : 0;
            stars.forEach(function(s, i) {
                s.style.color = '';
                if (i < currentRating) {
                    s.classList.remove('text-muted');
                    s.classList.add('text-warning');
                } else {
                    s.classList.remove('text-warning');
                    s.classList.add('text-muted');
                }
            });
        });
    });
}

/**
 * Initialize data tables with search and pagination
 */
function initializeDataTables() {
    // Simple search functionality for tables
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(function(input) {
        const tableId = input.dataset.table;
        const table = document.getElementById(tableId);
        if (!table) return;
        
        input.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Dashboard specific functionality
 */
function initializeDashboard() {
    // Animate counters on dashboard
    const counters = document.querySelectorAll('.counter');
    counters.forEach(function(counter) {
        animateCounter(counter);
    });
    
    // Auto-refresh dashboard data every 5 minutes
    if (window.location.pathname === '/dashboard') {
        setInterval(function() {
            refreshDashboardStats();
        }, 300000); // 5 minutes
    }
}

/**
 * Animate counter numbers
 */
function animateCounter(element) {
    const target = parseInt(element.textContent);
    const increment = target / 20;
    let current = 0;
    
    const timer = setInterval(function() {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 50);
}

/**
 * Refresh dashboard statistics (for auto-update)
 */
function refreshDashboardStats() {
    // This would typically make an AJAX call to get updated stats
    // For now, we'll just add a visual indicator that data is fresh
    const statsCards = document.querySelectorAll('.stats-card');
    statsCards.forEach(function(card) {
        card.style.opacity = '0.7';
        setTimeout(function() {
            card.style.opacity = '1';
        }, 200);
    });
}

/**
 * Utility functions
 */

// Format date for display
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Show loading state
function showLoading(element, message = 'Loading...') {
    const original = element.innerHTML;
    element.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${message}`;
    element.disabled = true;
    
    return function hideLoading() {
        element.innerHTML = original;
        element.disabled = false;
    };
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    setTimeout(function() {
        if (alertDiv.parentNode) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, duration);
}

// Confirm action with modal
function confirmAction(title, message, callback, confirmText = 'Confirm', cancelText = 'Cancel') {
    const modalId = 'confirmModal_' + Date.now();
    const modalHtml = `
        <div class="modal fade" id="${modalId}" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                        <button type="button" class="btn btn-primary confirm-btn">${confirmText}</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById(modalId);
    const bsModal = new bootstrap.Modal(modal);
    
    modal.querySelector('.confirm-btn').addEventListener('click', function() {
        callback();
        bsModal.hide();
    });
    
    modal.addEventListener('hidden.bs.modal', function() {
        modal.remove();
    });
    
    bsModal.show();
}

// Copy to clipboard
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    navigator.clipboard.writeText(text).then(function() {
        showNotification(successMessage, 'success', 2000);
    }).catch(function(err) {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'danger', 3000);
    });
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export utilities for global use
window.ReviewPro = {
    showNotification,
    confirmAction,
    copyToClipboard,
    showLoading,
    formatDate,
    debounce
};
