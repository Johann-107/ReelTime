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

// Function to display form errors
function showFormErrors(form, errors) {
    // Clear previous errors
    const existingErrors = form.querySelectorAll('.error-message');
    existingErrors.forEach(error => error.remove());
    
    // Remove error borders
    const inputs = form.querySelectorAll('.form-input');
    inputs.forEach(input => input.classList.remove('error'));
    
    // Display new errors
    for (const field in errors) {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            input.classList.add('error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.color = '#ff6b6b';
            errorDiv.style.fontSize = '0.8rem';
            errorDiv.style.marginTop = '0.25rem';
            errorDiv.textContent = errors[field][0].message;
            input.parentNode.appendChild(errorDiv);
        }
    }
}

// Make messages available
window.messages = {
    success: function(msg) {
        console.log('Success:', msg);
        alert(msg);
    },
    error: function(msg) {
        console.error('Error:', msg);
        alert(msg);
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
        const existingErrors = this.querySelectorAll('.error-message');
        existingErrors.forEach(error => error.remove());
        const inputs = this.querySelectorAll('.form-input');
        inputs.forEach(input => input.classList.remove('error'));
        
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            console.log(`${formName} AJAX response status:`, response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`${formName} AJAX response data:`, data);
            if (data.success) {
                console.log(`${formName} successful!`);
                if (formName === 'registration') {
                    closeRegisterModal();
                } else if (formName === 'admin registration') {
                    closeAdminRegisterModal();
                    messages.success(data.message || 'Admin registration successful!');
                }
                
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/?show_login=true';
                }, 100);
            } else {
                console.log(`${formName} failed`);
                if (data.errors) {
                    showFormErrors(form, data.errors);
                } else if (data.message) {
                    messages.error(data.message);
                }
            }
        })
        .catch(error => {
            console.error(`${formName} AJAX Error:`, error);
            messages.error(`An error occurred during ${formName}. Please try again.`);
        })
        .finally(() => {
            isSubmitting = false;
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        });
        
        return false;
    });
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