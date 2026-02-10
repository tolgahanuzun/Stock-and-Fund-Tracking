const Auth = {
    tokenKey: 'auth_token',
    
    // Login
    async login(username, password) {
        try {
            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem(this.tokenKey, data.access_token);
                return { success: true };
            } else {
                return { success: false, message: data.detail || 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Network error' };
        }
    },
    
    // Register
    async register(username, password, fullName) {
        try {
            const response = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    username, 
                    password, 
                    full_name: fullName 
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Auto login on register? Or return success.
                // The API returns the token on register too in my implementation.
                localStorage.setItem(this.tokenKey, data.access_token);
                return { success: true };
            } else {
                return { success: false, message: data.detail || 'Registration failed' };
            }
        } catch (error) {
            console.error('Register error:', error);
            return { success: false, message: 'Network error' };
        }
    },
    
    // Logout
    logout() {
        localStorage.removeItem(this.tokenKey);
        window.location.href = '/static/login.html';
    },
    
    // Get Token
    getToken() {
        return localStorage.getItem(this.tokenKey);
    },
    
    // Check if authenticated
    isAuthenticated() {
        return !!this.getToken();
    },
    
    // Require Auth (Redirect if not)
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/static/login.html';
            return false;
        }
        return true;
    },
    
    // Get Auth Headers
    getHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
    },
    
    // Handle 401
    handleUnauthorized() {
        this.logout();
    }
};
