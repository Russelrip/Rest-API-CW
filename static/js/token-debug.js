document.addEventListener('DOMContentLoaded', function() {
    // Comprehensive Token Debugging Fetch
    function debugFetch(url, options = {}) {
        const accessToken = localStorage.getItem('access_token');
        
        console.group('Fetch Debug');
        console.log('URL:', url);
        console.log('Access Token:', accessToken);
        
        // Detailed headers logging
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        };
        
        console.log('Request Headers:', headers);

        return fetch(url, {
            ...options,
            headers: headers
        }).then(response => {
            console.log('Response Status:', response.status);
            console.log('Response Headers:', Object.fromEntries(response.headers.entries()));
            
            // Log response body for debugging
            if (!response.ok) {
                return response.text().then(text => {
                    console.error('Error Response Body:', text);
                    throw new Error(text);
                });
            }
            
            console.groupEnd();
            return response;
        });
    }

    // Replace standard fetch with debug version
    window.originalFetch = window.fetch;
    window.fetch = debugFetch;

    // Token Validation Utility
    function validateToken() {
        const accessToken = localStorage.getItem('access_token');
        
        if (!accessToken) {
            console.warn('No access token found');
            return false;
        }

        try {
            const tokenParts = accessToken.split('.');
            
            if (tokenParts.length !== 3) {
                console.error('Invalid token format');
                return false;
            }

            const payload = JSON.parse(atob(tokenParts[1]));
            const currentTime = Math.floor(Date.now() / 1000);

            console.group('Token Validation');
            console.log('Token Payload:', payload);
            console.log('Current Time:', currentTime);
            console.log('Token Expiration:', payload.exp);

            if (payload.exp && payload.exp < currentTime) {
                console.error('Token has expired');
                return false;
            }

            console.log('Token is valid');
            console.groupEnd();
            return true;
        } catch (error) {
            console.error('Token validation error:', error);
            return false;
        }
    }

    // Automatic Token Refresh
    async function refreshAccessToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
            console.error('No refresh token found');
            window.location.href = '/login';
            return null;
        }

        try {
            console.log('Attempting to refresh access token');

            const response = await fetch('/auth/refresh', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${refreshToken}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log('Refresh Response Status:', response.status);

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            
            console.log('New access token received');
            localStorage.setItem('access_token', data.access_token);

            return data.access_token;
        } catch (error) {
            console.error('Token refresh error:', error);
            window.location.href = '/login';
            return null;
        }
    }

    // Expose utilities globally for debugging
    window.tokenDebug = {
        validateToken,
        refreshAccessToken
    };

    // Initial token validation
    validateToken();
});