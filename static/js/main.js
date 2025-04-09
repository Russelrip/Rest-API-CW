/**
 * Main JavaScript for the Countries API Service
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication status and update navigation
    updateAuthStatus();
    
    // Setup logout functionality
    setupLogout();
});

/**
 * Update navigation based on authentication status
 */
function updateAuthStatus() {
    const isLoggedIn = Boolean(localStorage.getItem('access_token'));
    
    // Get navigation elements
    const loginLink = document.getElementById('login-link');
    const registerLink = document.getElementById('register-link');
    const dashboardLink = document.getElementById('dashboard-link');
    const logoutLink = document.getElementById('logout-link');
    
    if (isLoggedIn) {
        // User is logged in - show dashboard and logout links
        if (loginLink) loginLink.classList.add('d-none');
        if (registerLink) registerLink.classList.add('d-none');
        if (dashboardLink) dashboardLink.classList.remove('d-none');
        if (logoutLink) logoutLink.classList.remove('d-none');
        
        // Check if token is expired
        checkTokenExpiration();
    } else {
        // User is not logged in - show login and register links
        if (loginLink) loginLink.classList.remove('d-none');
        if (registerLink) registerLink.classList.remove('d-none');
        if (dashboardLink) dashboardLink.classList.add('d-none');
        if (logoutLink) logoutLink.classList.add('d-none');
    }
}

/**
 * Setup logout functionality
 */
function setupLogout() {
    const logoutLink = document.getElementById('logout-link');
    
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
}

/**
 * Logout function to clear credentials and redirect
 */
function logout() {
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    // Redirect to login page
    window.location.href = '/login';
}

/**
 * Check if token is expired and handle refresh if needed
 */
function checkTokenExpiration() {
    // Get the token and parse it
    const token = localStorage.getItem('access_token');
    
    if (!token) return;
    
    // Parse JWT payload
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expTime = payload.exp * 1000; // Convert to milliseconds
        const currentTime = Date.now();
        
        // If token is expired or will expire in the next 5 minutes
        if (expTime - currentTime < 5 * 60 * 1000) {
            refreshToken();
        }
    } catch (error) {
        console.error('Error parsing JWT:', error);
        // If there's an error, try refreshing the token
        refreshToken();
    }
}

/**
 * Refresh the authentication token
 */
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
        // No refresh token, redirect to login
        window.location.href = '/login';
        return;
    }
    
    try {
        const response = await fetch('/auth/refresh', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${refreshToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
        } else {
            // Refresh failed, redirect to login
            localStorage.clear();
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
        // Network error, but don't redirect yet
    }
}

/**
 * Show an alert message to the user
 * @param {string} message - The message to display
 * @param {string} type - The type of alert (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            if (alertsContainer.contains(alert)) {
                alertsContainer.removeChild(alert);
            }
        }, 150);
    }, 5000);
}