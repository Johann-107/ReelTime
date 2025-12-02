// Calculate scrollbar width to prevent layout shift
function getScrollbarWidth() {
    const outer = document.createElement('div');
    outer.style.visibility = 'hidden';
    outer.style.overflow = 'scroll';
    document.body.appendChild(outer);
    
    const inner = document.createElement('div');
    outer.appendChild(inner);
    
    const scrollbarWidth = outer.offsetWidth - inner.offsetWidth;
    
    outer.parentNode.removeChild(outer);
    
    return scrollbarWidth;
}

// Set scrollbar width as CSS variable
function setScrollbarWidth() {
    const scrollbarWidth = getScrollbarWidth();
    document.documentElement.style.setProperty('--scrollbar-width', `${scrollbarWidth}px`);
}

// Password toggle functionality
function initPasswordToggles() {
    console.log('Initializing password toggles...');
    
    const toggles = [
        { toggleId: 'toggleLoginPassword', inputId: 'login_password_modal', name: 'login' },
        { toggleId: 'toggleRegisterPassword', inputId: 'register_password_modal', name: 'register' },
        { toggleId: 'toggleRegisterConfirmPassword', inputId: 'confirm_password_modal', name: 'register confirm' }
    ];

    toggles.forEach(({ toggleId, inputId, name }) => {
        const toggle = document.getElementById(toggleId);
        const input = document.getElementById(inputId);
        
        if (toggle && input) {
            console.log(`Found ${name} password toggle`);
            toggle.addEventListener('click', function() {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                this.classList.toggle('password-visible');
                console.log(`${name} password toggled to:`, type);
            });
        } else {
            console.log(`${name} password toggle elements not found`);
        }
    });
}

// Generic modal functions
function createModalFunctions(modalId, openFuncName, closeFuncName) {
    return {
        open: function() {
            console.log(`${openFuncName} called`);
            const modal = document.getElementById(modalId);
            if (modal) {
                console.log(`${modalId} found, opening...`);
                setScrollbarWidth();
                modal.style.display = 'flex';
                modal.style.opacity = '1';
                modal.style.visibility = 'visible';
                modal.style.zIndex = '9999';
                document.body.classList.add('modal-open');
                
                setTimeout(() => {
                    modal.style.display = 'flex';
                }, 10);
            } else {
                console.log(`${modalId} NOT found`);
            }
        },
        close: function() {
            console.log(`${closeFuncName} called`);
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'none';
                document.body.classList.remove('modal-open');
                document.documentElement.style.setProperty('--scrollbar-width', '0px');
            }
        }
    };
}

// Create modal functions
const loginModal = createModalFunctions('loginModal', 'openLoginModal', 'closeLoginModal');
const registerModal = createModalFunctions('registerModal', 'openRegisterModal', 'closeRegisterModal');
const adminRegisterModal = createModalFunctions('adminRegisterModal', 'openAdminRegisterModal', 'closeAdminRegisterModal');

// Assign to global functions
function openLoginModal() { loginModal.open(); }
function closeLoginModal() { loginModal.close(); }
function openRegisterModal() { registerModal.open(); }
function closeRegisterModal() { registerModal.close(); }
function openAdminRegisterModal() { adminRegisterModal.open(); }
function closeAdminRegisterModal() { adminRegisterModal.close(); }

// Make messages available
window.messages = {
    success: function(msg) {
        console.log('Success:', msg);
        alert('✓ ' + msg);
    },
    error: function(msg) {
        console.error('Error:', msg);
        alert('✗ ' + msg);
    }
};

// Check if we're on a movie list page
function isMovieListPage() {
    const isMoviePage = document.getElementById('movieGrid') || 
                       document.querySelector('.movie-grid') ||
                       window.location.pathname.includes('/movies/');
    console.log('isMovieListPage:', isMoviePage);
    return isMoviePage;
}

// Generic form submission handler
function handleFormSubmission(form, formName) {
    let isSubmitting = false;
    
    form.addEventListener('submit', function(e) {
        if (isSubmitting) {
            e.preventDefault();
            e.stopImmediatePropagation();
            console.log(`${formName} already submitting, preventing duplicate`);
            return false;
        }
        
        isSubmitting = true;
        e.preventDefault();
        e.stopImmediatePropagation();
        
        console.log(`Starting AJAX ${formName}...`);
        
        const formData = new FormData(this);
        const submitButton = this.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        // Show loading state
        submitButton.textContent = `${formName}...`;
        submitButton.disabled = true;
        
        // Clear previous errors
        clearFormErrors(form);
        
        // Debug: Log what we're sending
        console.log('Sending to:', this.action);
        console.log('Form data:', Object.fromEntries(formData.entries()));
        
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            }
        })
        .then(response => {
            console.log(`${formName} AJAX response status:`, response.status);
            console.log('Content-Type:', response.headers.get('content-type'));
            
            // Get response as text first
            return response.text().then(text => {
                console.log(`${formName} response length:`, text.length);
                console.log(`${formName} response (first 200 chars):`, text.substring(0, 200));
                
                // Try to parse as JSON
                try {
                    const data = JSON.parse(text);
                    console.log(`${formName} parsed as JSON:`, data);
                    return { status: response.status, data: data, type: 'json' };
                } catch (e) {
                    console.log(`${formName} not JSON, treating as HTML/text`);
                    return { status: response.status, data: text, type: 'html' };
                }
            });
        })
        .then(result => {
            console.log(`${formName} result type:`, result.type, 'data:', result.data);
            
            if (result.type === 'json') {
                handleJsonResponse(form, formName, result.data, result.status);
            } else {
                handleHtmlResponse(form, formName, result.data, result.status);
            }
        })
        .catch(error => {
            console.error(`${formName} AJAX Error:`, error);
            messages.error(`Network error during ${formName}. Please check your connection.`);
        })
        .finally(() => {
            setTimeout(() => {
                isSubmitting = false;
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }, 1000);
        });
        
        return false;
    });
}

// Handle JSON responses
function handleJsonResponse(form, formName, data, status) {
    if (data.success) {
        console.log(`${formName} successful!`);
        if (formName === 'registration') {
            closeRegisterModal();
            messages.success(data.message || 'Registration successful! Please log in.');
        } else if (formName === 'admin registration') {
            closeAdminRegisterModal();
            messages.success(data.message || 'Admin registration successful!');
        }
        
        setTimeout(() => {
            window.location.href = data.redirect_url || '/?show_login=true';
        }, 100);
    } else {
        console.log(`${formName} failed with JSON errors`);
        if (data.errors) {
            showFormErrors(form, data.errors);
        } else if (data.message) {
            messages.error(data.message);
        } else {
            messages.error('An error occurred. Please try again.');
        }
    }
}

// Handle HTML responses (Django is returning form HTML with errors)
function handleHtmlResponse(form, formName, html, status) {
    console.log('Handling HTML response for', formName);
    
    if (status === 400) {
        // Extract errors from Django's HTML error list
        const errors = extractErrorsFromHtml(html);
        console.log('Extracted errors from HTML:', errors);
        
        if (Object.keys(errors).length > 0) {
            showFormErrors(form, errors);
        } else {
            // Fallback error message
            messages.error('Please check your form for errors.');
        }
    } else {
        messages.error(`Server error (${status}). Please try again.`);
    }
}

// Extract Django form errors from HTML
function extractErrorsFromHtml(html) {
    const errors = {};
    console.log('Parsing HTML for errors...');
    
    // Create a temporary DOM to parse the HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Look for Django error lists
    const errorLists = doc.querySelectorAll('.errorlist');
    console.log('Found error lists:', errorLists.length);
    
    errorLists.forEach(errorList => {
        // Get the field name from parent structure
        let fieldName = '';
        let fieldErrors = [];
        
        // The structure: <li>field_name<ul class="errorlist">...</ul></li>
        const listItem = errorList.parentElement;
        
        if (listItem && listItem.tagName === 'LI') {
            // The field name should be the text content of the <li> before the <ul>
            const fullText = listItem.textContent || '';
            
            // Try to extract field name
            const lines = fullText.split('\n').filter(line => line.trim());
            if (lines.length > 0) {
                // Look for common field names
                const possibleFieldNames = ['phone_number', 'password', 'email', 'username', 'first_name', 'last_name'];
                
                for (const possibleField of possibleFieldNames) {
                    if (fullText.toLowerCase().includes(possibleField)) {
                        fieldName = possibleField;
                        break;
                    }
                }
                
                // If not found by name, try to get it from the text
                if (!fieldName && lines[0]) {
                    fieldName = lines[0].trim().toLowerCase().replace(/ /g, '_');
                }
            }
        }
        
        // Get all error messages from the <ul>
        const errorItems = errorList.querySelectorAll('li');
        errorItems.forEach(item => {
            fieldErrors.push(item.textContent.trim());
        });
        
        // If we found field name and errors, add to errors object
        if (fieldName && fieldErrors.length > 0) {
            errors[fieldName] = fieldErrors;
            console.log(`Found errors for ${fieldName}:`, fieldErrors);
        } else if (fieldErrors.length > 0) {
            // If we have errors but no field name, treat as general errors
            errors['__all__'] = fieldErrors;
            console.log('Found general errors:', fieldErrors);
        }
    });
    
    // Also check for individual error fields by ID
    const errorFields = doc.querySelectorAll('[id$="_error"]');
    errorFields.forEach(errorField => {
        const id = errorField.id;
        const fieldMatch = id.match(/id_(.+)_error/);
        if (fieldMatch) {
            const fieldName = fieldMatch[1];
            const errorMessages = [];
            errorField.querySelectorAll('li').forEach(item => {
                errorMessages.push(item.textContent.trim());
            });
            if (errorMessages.length > 0) {
                errors[fieldName] = errorMessages;
            }
        }
    });
    
    console.log('Final extracted errors:', errors);
    return errors;
}

// Clear all form errors
function clearFormErrors(form) {
    const existingErrors = form.querySelectorAll('.error-message, .alert-danger');
    existingErrors.forEach(error => error.remove());
    
    const inputs = form.querySelectorAll('.form-input, input, select, textarea');
    inputs.forEach(input => {
        input.classList.remove('error');
        input.style.borderColor = '';
    });
}

// Enhanced showFormErrors function
function showFormErrors(form, errors) {
    console.log('showFormErrors called with:', errors);
    
    // Clear previous errors
    clearFormErrors(form);
    
    // Display new errors
    for (const field in errors) {
        if (field === '__all__' || field === 'non_field_errors') {
            // Display general errors
            const generalErrorDiv = document.createElement('div');
            generalErrorDiv.className = 'error-message general-error';
            generalErrorDiv.style.cssText = `
                background-color: #ffebee;
                color: #c62828;
                padding: 12px;
                margin-bottom: 15px;
                border-radius: 4px;
                border: 1px solid #ffcdd2;
                text-align: center;
                font-weight: 600;
            `;
            
            const errorMessages = Array.isArray(errors[field]) 
                ? errors[field] 
                : [errors[field]];
            
            generalErrorDiv.textContent = errorMessages.join(', ');
            form.prepend(generalErrorDiv);
            continue;
        }
        
        // Find the input field
        let input = form.querySelector(`[name="${field}"]`);
        
        if (!input) {
            // Try variations for Django field names
            input = form.querySelector(`[name*="${field}"]`) ||
                    form.querySelector(`#id_${field}`) ||
                    form.querySelector(`#${field}`);
        }
        
        if (input) {
            input.classList.add('error');
            input.style.borderColor = '#ff6b6b';
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.color = '#ff6b6b';
            errorDiv.style.fontSize = '0.8rem';
            errorDiv.style.marginTop = '0.25rem';
            errorDiv.style.fontWeight = '500';
            
            const errorMessages = Array.isArray(errors[field]) 
                ? errors[field] 
                : [errors[field]];
            
            errorDiv.textContent = errorMessages.join(', ');
            input.parentNode.appendChild(errorDiv);
            
            console.log(`Displayed error for ${field}:`, errorMessages);
        } else {
            console.warn(`Could not find input for field: ${field}`);
        }
    }
    
    // Scroll to first error
    const firstError = form.querySelector('.error');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

// Initialize modal event listeners
function initModal() {
    console.log('initModal called');
    
    // Initialize password toggles first
    initPasswordToggles();
    
    // Modal configurations
    const modals = [
        { id: 'loginModal', closeId: 'closeLoginModal', closeFunc: closeLoginModal },
        { id: 'registerModal', closeId: 'closeRegisterModal', closeFunc: closeRegisterModal },
        { id: 'adminRegisterModal', closeId: 'closeAdminRegisterModal', closeFunc: closeAdminRegisterModal }
    ];

    // Set up modal event listeners
    modals.forEach(({ id, closeId, closeFunc }) => {
        const closeButton = document.getElementById(closeId);
        const modal = document.getElementById(id);
        
        if (closeButton) {
            closeButton.addEventListener('click', closeFunc);
        }
        
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeFunc();
                }
            });
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeLoginModal();
            closeRegisterModal();
            closeAdminRegisterModal();
        }
    });

    // Form submissions
    const registerForm = document.getElementById('registerFormModal');
    if (registerForm) {
        handleFormSubmission(registerForm, 'registration');
    }

    const adminRegisterForm = document.getElementById('adminRegisterFormModal');
    if (adminRegisterForm) {
        handleFormSubmission(adminRegisterForm, 'admin registration');
    }

    // Auto-open modals based on URL parameters - BUT NOT ON MOVIE LIST PAGES
    const urlParams = new URLSearchParams(window.location.search);
    const shouldShowLogin = urlParams.get('show_login') === 'true';
    const shouldShowRegister = urlParams.get('show_register') === 'true';
    
    console.log('URL params - show_login:', shouldShowLogin, 'show_register:', shouldShowRegister);
    console.log('Is movie list page:', isMovieListPage());
    
    // Only auto-open modals if we're NOT on a movie list page
    if (!isMovieListPage()) {
        if (shouldShowLogin) {
            console.log('Auto-opening login modal');
            setTimeout(() => openLoginModal(), 100);
        }
        if (shouldShowRegister) {
            console.log('Auto-opening register modal');
            setTimeout(() => openRegisterModal(), 100);
        }
    } else if (shouldShowLogin || shouldShowRegister) {
        console.log('Prevented auto-modal open on movie list page');
    }
}

// Make functions globally available
window.openLoginModal = openLoginModal;
window.closeLoginModal = closeLoginModal;
window.openRegisterModal = openRegisterModal;
window.closeRegisterModal = closeRegisterModal;
window.openAdminRegisterModal = openAdminRegisterModal;
window.closeAdminRegisterModal = closeAdminRegisterModal;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - modal.js initializing');
    setScrollbarWidth();
    initModal();
});

// Auto-open modals based on URL parameters
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('show_login') === 'true') {
    console.log('Auto-opening login modal from URL parameter');
    setTimeout(() => openLoginModal(), 500);
}