document.addEventListener('DOMContentLoaded', function() {
    // Token Management Utility
    const tokenManager = {
        getAccessToken() {
            return localStorage.getItem('access_token');
        },

        async secureRequest(url, options = {}) {
            const accessToken = this.getAccessToken();

            if (!accessToken) {
                console.error('No access token found');
                window.location.href = '/login';
                return null;
            }

            const headers = {
                ...options.headers,
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            };

            try {
                const response = await fetch(url, { ...options, headers });

                if (response.status === 401) {
                    console.log('Token expired, attempting to refresh');
                    const newToken = await this.refreshAccessToken();
                    
                    if (newToken) {
                        headers['Authorization'] = `Bearer ${newToken}`;
                        return fetch(url, { ...options, headers });
                    }
                }

                return response;
            } catch (error) {
                console.error('Secure request error:', error);
                return null;
            }
        },

        async refreshAccessToken() {
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                
                const response = await fetch('/auth/refresh', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${refreshToken}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error('Token refresh failed');
                }

                const { access_token } = await response.json();
                localStorage.setItem('access_token', access_token);
                return access_token;
            } catch (error) {
                console.error('Token refresh error:', error);
                window.location.href = '/login';
                return null;
            }
        }
    };

    // Dashboard-specific logic can be added here
});