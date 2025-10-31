/**
 * Enhanced Utility Functions for Student Tracking System
 * Common functions used across the application
 */

// Global utility object
window.TimetableUtils = {
    
    // Show loading state for buttons
    setButtonLoading: function(button, isLoading = true) {
        if (isLoading) {
            button.dataset.originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || 'Submit';
        }
    },
    
    // Enhanced toast notifications
    showNotification: function(message, type = 'info', duration = 5000) {
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${this.getIconForType(type)} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // Create toast container if it doesn't exist
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        // Create and show toast
        const toastElement = document.createElement('div');
        toastElement.innerHTML = toastHTML;
        const toast = toastElement.firstElementChild;
        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();
        
        // Remove after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    // Get icon for notification type
    getIconForType: function(type) {
        const iconMap = {
            'success': 'check-circle',
            'danger': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'primary': 'info-circle'
        };
        return iconMap[type] || 'info-circle';
    },
    
    // Confirm dialog with custom styling
    confirmDialog: function(message, title = 'Confirm Action') {
        return new Promise((resolve) => {
            const modalHTML = `
                <div class="modal fade" id="confirmModal" tabindex="-1">
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
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-danger" id="confirmYes">Confirm</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal
            const existingModal = document.getElementById('confirmModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to body
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            const modal = document.getElementById('confirmModal');
            const bsModal = new bootstrap.Modal(modal);
            
            // Handle events
            document.getElementById('confirmYes').addEventListener('click', () => {
                bsModal.hide();
                resolve(true);
            });
            
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
                resolve(false);
            });
            
            bsModal.show();
        });
    },
    
    // Format date for display
    formatDate: function(dateString, format = 'short') {
        const date = new Date(dateString);
        const options = {
            short: { year: 'numeric', month: 'short', day: 'numeric' },
            long: { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                weekday: 'long' 
            },
            time: { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: true 
            }
        };
        
        return date.toLocaleDateString('en-US', options[format] || options.short);
    },
    
    // Format time for display
    formatTime: function(timeString) {
        const [hours, minutes] = timeString.split(':');
        const date = new Date();
        date.setHours(parseInt(hours), parseInt(minutes));
        return date.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    },
    
    // Validate form fields
    validateForm: function(formElement) {
        let isValid = true;
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        });
        
        return isValid;
    },
    
    // AJAX helper with error handling
    apiCall: function(url, options = {}) {
        const defaults = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
            }
        };
        
        const config = Object.assign(defaults, options);
        
        return fetch(url, config)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API call failed:', error);
                this.showNotification('An error occurred. Please try again.', 'danger');
                throw error;
            });
    },
    
    // Debounce function for search inputs
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Copied to clipboard!', 'success');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showNotification('Copied to clipboard!', 'success');
        }
    },
    
    // Initialize common event listeners
    initialize: function() {
        // Initialize tooltips
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
        
        // Initialize popovers
        document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
            new bootstrap.Popover(el);
        });
        
        // Add form validation classes on submit
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showNotification('Please fill in all required fields.', 'warning');
                }
                form.classList.add('was-validated');
            });
        });
        
        // Auto-hide alerts (safe close to avoid remove() on null)
        setTimeout(() => {
            document.querySelectorAll('.alert:not(.alert-permanent)').forEach((alertEl) => {
                if (!alertEl || !document.body.contains(alertEl)) return;
                try {
                    const bsAlert = bootstrap.Alert.getInstance(alertEl) || new bootstrap.Alert(alertEl);
                    bsAlert && bsAlert.close();
                } catch (e) {
                    try { alertEl.remove && alertEl.remove(); } catch (_) {}
                }
            });
        }, 5000);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape to close modals
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    const bsModal = bootstrap.Modal.getInstance(openModal);
                    bsModal?.hide();
                }
            }
            
            // Ctrl+/ for help (if help modal exists)
            if (e.ctrlKey && e.key === '/') {
                const helpModal = document.getElementById('helpModal');
                if (helpModal) {
                    const bsModal = new bootstrap.Modal(helpModal);
                    bsModal.show();
                }
            }
        });
    },
    
    // Create loading spinner
    createSpinner: function(size = 'md') {
        const sizeClasses = {
            'sm': 'spinner-border-sm',
            'md': '',
            'lg': 'spinner-border-lg'
        };
        
        return `<div class="spinner-border ${sizeClasses[size]}" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>`;
    },
    
    // Show/hide page loading overlay
    togglePageLoading: function(show = true) {
        let overlay = document.getElementById('page-loading-overlay');
        
        if (show) {
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.id = 'page-loading-overlay';
                overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
                overlay.style.cssText = 'background: rgba(255,255,255,0.8); z-index: 9998;';
                overlay.innerHTML = `
                    <div class="text-center">
                        ${this.createSpinner('lg')}
                        <div class="mt-3">Loading...</div>
                    </div>
                `;
                document.body.appendChild(overlay);
            }
            overlay.style.display = 'flex';
        } else if (overlay) {
            overlay.style.display = 'none';
        }
    },
    
    // Enhanced table search functionality
    initializeTableSearch: function(tableId, searchInputId) {
        const table = document.getElementById(tableId);
        const searchInput = document.getElementById(searchInputId);
        
        if (!table || !searchInput) return;
        
        const debouncedSearch = this.debounce((query) => {
            const rows = table.querySelectorAll('tbody tr');
            const searchTerm = query.toLowerCase();
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
            
            // Show "no results" message if needed
            const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
            let noResultsRow = table.querySelector('.no-results-row');
            
            if (visibleRows.length === 0 && searchTerm) {
                if (!noResultsRow) {
                    const colCount = table.querySelectorAll('thead th').length;
                    noResultsRow = document.createElement('tr');
                    noResultsRow.className = 'no-results-row';
                    noResultsRow.innerHTML = `<td colspan="${colCount}" class="text-center text-muted py-4">No results found</td>`;
                    table.querySelector('tbody').appendChild(noResultsRow);
                }
                noResultsRow.style.display = '';
            } else if (noResultsRow) {
                noResultsRow.style.display = 'none';
            }
        }, 300);
        
        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    TimetableUtils.initialize();
});

// Make functions available globally for backward compatibility
window.showToast = TimetableUtils.showNotification;
window.setButtonLoading = TimetableUtils.setButtonLoading;
window.handleApiError = function(error, message) {
    console.error('API Error:', error);
    TimetableUtils.showNotification(message || 'An error occurred', 'danger');
};
