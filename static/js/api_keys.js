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

            // Merge headers, ensuring Authorization is set
            const headers = {
                ...options.headers,
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            };

            try {
                const response = await fetch(url, {
                    ...options,
                    headers
                });

                // Handle token expiration
                if (response.status === 401) {
                    console.log('Token expired, attempting to refresh');
                    const newToken = await this.refreshAccessToken();
                    
                    if (newToken) {
                        // Update headers with new token
                        headers['Authorization'] = `Bearer ${newToken}`;
                        
                        // Retry the request
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

    // API Key Management
    const apiKeyManager = {
        // Load API Keys
        async loadApiKeys() {
            try {
                // Use secureRequest instead of fetch
                const response = await tokenManager.secureRequest('/user/api-keys', {
                    method: 'GET'
                });

                if (!response) {
                    throw new Error('Failed to load API keys');
                }

                const data = await response.json();
                this.renderApiKeys(data.api_keys);
            } catch (error) {
                console.error('API keys load error:', error);
                this.showAlert('Failed to load API keys. Please try again.', 'danger');
            }
        },

        // Create API Key
        async createApiKey() {
            const keyName = document.getElementById('key-name').value.trim();
            const expirationDays = document.getElementById('key-expiration').value;

            try {
                // Use secureRequest for creating API key
                const response = await tokenManager.secureRequest('/user/api-keys', {
                    method: 'POST',
                    body: JSON.stringify({
                        name: keyName || undefined,
                        expires_in_days: parseInt(expirationDays)
                    })
                });

                if (!response) {
                    throw new Error('Failed to create API key');
                }

                const data = await response.json();

                // Close create key modal
                bootstrap.Modal.getInstance(document.getElementById('createKeyModal')).hide();

                // Show new key in display modal
                document.getElementById('new-key-display').value = data.api_key.key;
                const newKeyModal = new bootstrap.Modal(document.getElementById('newKeyModal'));
                newKeyModal.show();

                // Reload API keys
                this.loadApiKeys();

                this.showAlert('API key created successfully', 'success');
            } catch (error) {
                console.error('API key creation error:', error);
                this.showAlert('Failed to create API key. Please try again.', 'danger');
            }
        },

        // Revoke API Key
        async revokeApiKey(keyId) {
            try {
                // Use secureRequest for revoking API key
                const response = await tokenManager.secureRequest(`/user/api-keys/${keyId}`, {
                    method: 'DELETE'
                });

                if (!response) {
                    throw new Error('Failed to revoke API key');
                }

                // Close revoke confirmation modal
                bootstrap.Modal.getInstance(document.getElementById('revokeKeyModal')).hide();

                // Reload API keys
                this.loadApiKeys();

                this.showAlert('API key revoked successfully', 'success');
            } catch (error) {
                console.error('API key revocation error:', error);
                this.showAlert('Failed to revoke API key. Please try again.', 'danger');
            }
        },

        // Render API Keys in Table
        renderApiKeys(keys) {
            const keysList = document.getElementById('keys-list');
            keysList.innerHTML = ''; // Clear existing keys

            keys.forEach(key => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${key.name || '<em>Unnamed</em>'}</td>
                    <td>${new Date(key.created_at).toLocaleDateString()}</td>
                    <td>${key.expires_at ? new Date(key.expires_at).toLocaleDateString() : 'Never'}</td>
                    <td>${key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}</td>
                    <td>
                        <span class="badge ${key.is_active ? 'bg-success' : 'bg-danger'}">
                            ${key.is_active ? 'Active' : 'Revoked'}
                        </span>
                    </td>
                    <td>
                        ${key.is_active ? 
                            `<button class="btn btn-sm btn-danger revoke-key" data-key-id="${key.id}">
                                Revoke
                            </button>` : 
                            '<em>Revoked</em>'
                        }
                    </td>
                `;
                keysList.appendChild(row);
            });
        },

        // Show Alerts
        showAlert(message, type = 'info') {
            const alertContainer = document.getElementById('alerts-container');
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            alertContainer.appendChild(alertDiv);

            // Auto-dismiss
            setTimeout(() => {
                bootstrap.Alert.getOrCreateInstance(alertDiv).close();
            }, 5000);
        },

        // Initialize Event Listeners
        initEventListeners() {
            // Create key button
            document.getElementById('confirm-create-key').addEventListener('click', () => {
                this.createApiKey();
            });

            // Revoke key delegation
            document.getElementById('keys-table-container').addEventListener('click', (event) => {
                const revokeButton = event.target.closest('.revoke-key');
                if (revokeButton) {
                    const keyId = revokeButton.dataset.keyId;
                    
                    // Show confirmation modal
                    const revokeModal = new bootstrap.Modal(document.getElementById('revokeKeyModal'));
                    revokeModal.show();

                    // Set up confirm revocation
                    document.getElementById('confirm-revoke-key').onclick = () => {
                        this.revokeApiKey(keyId);
                    };
                }
            });
        },

        // Initialize the page
        init() {
            // Initial load of API keys
            this.loadApiKeys();
            
            // Set up event listeners
            this.initEventListeners();
        }
    };

    // Initialize API key management
    apiKeyManager.init();
});