from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
import logging

web_bp = Blueprint('web', __name__)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define a custom decorator that renders templates even if JWT is missing
def optional_jwt(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        try:
            # Try to verify the JWT, but continue even if it fails
            verify_jwt_in_request()
            current_app.logger.info("JWT verified successfully")
        except Exception as e:
            # Log but don't stop execution
            current_app.logger.info(f"JWT verification failed: {str(e)}")
        
        # Always continue to the route function
        return route_function(*args, **kwargs)
    return wrapper

@web_bp.route('/')
def index():
    """Render the homepage"""
    return render_template('base.html')

@web_bp.route('/login')
def login():
    """Render the login page"""
    return render_template('auth/login.html')

@web_bp.route('/register')
def register():
    """Render the registration page"""
    return render_template('auth/register.html')

@web_bp.route('/dashboard')
@optional_jwt
def dashboard():
    """Render the dashboard page"""
    current_app.logger.info("Accessing dashboard page")
    return render_template('dashboard/index.html')

@web_bp.route('/dashboard/api-keys')
@optional_jwt
def api_keys():
    """Render the API keys management page"""
    current_app.logger.info("Accessing API keys page")
    return render_template('dashboard/api_keys.html')

@web_bp.route('/dashboard/api-keys-minimal')
def api_keys_minimal():
    """Render a minimal API keys page for testing"""
    current_app.logger.info("Accessing minimal API keys page")
    return render_template('dashboard/api_keys_minimal.html')

@web_bp.route('/dashboard/profile')
@optional_jwt
def profile():
    """Render the user profile page"""
    current_app.logger.info("Accessing profile page")
    return render_template('dashboard/profile.html')

@web_bp.route('/docs')
def docs():
    """Render the API documentation page"""
    return render_template('docs.html')

# API protected routes - these still need JWT
@web_bp.route('/dashboard/check-auth')
@jwt_required()
def check_auth():
    """Simple endpoint to check authentication"""
    current_user_id = get_jwt_identity()
    current_app.logger.info(f"Authentication check for user ID: {current_user_id}")
    return jsonify({"authenticated": True, "user_id": current_user_id})

@web_bp.route('/debug/token-info')
def debug_token_info():
    """Show JWT configuration and create a test token"""
    from flask_jwt_extended import create_access_token
    import jwt
    
    # Get JWT config
    jwt_secret = current_app.config['JWT_SECRET_KEY']
    
    # Create a test token with a string subject
    test_token = create_access_token(identity="test-user")
    
    # Manual decode to verify 
    try:
        decoded = jwt.decode(
            test_token, 
            jwt_secret,
            algorithms=["HS256"]
        )
        manual_decode_success = True
    except Exception as e:
        decoded = {"error": str(e)}
        manual_decode_success = False
    
    return jsonify({
        "jwt_config": {
            "secret_key_prefix": jwt_secret[:10] + "...",
            "algorithm": "HS256",
            "token_location": current_app.config.get('JWT_TOKEN_LOCATION', ['headers']),
            "header_name": current_app.config.get('JWT_HEADER_NAME', 'Authorization'),
            "header_type": current_app.config.get('JWT_HEADER_TYPE', 'Bearer')
        },
        "test_token": {
            "token": test_token,
            "decoded": decoded,
            "manual_decode_success": manual_decode_success
        }
    })