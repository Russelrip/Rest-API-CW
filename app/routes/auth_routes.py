from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, 
    create_refresh_token, get_jwt_identity
)
from app.services.auth_service import auth_service
from app.utils.validators import validate_username, validate_email_address, validate_password
from app.utils.helpers import format_response, error_response

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        
        if not data:
            return error_response("No input data provided", 400)
        
        # Extract input fields
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validate username
        valid_username, username_msg = validate_username(username)
        if not valid_username:
            return error_response(username_msg, 400)
        
        # Validate email
        valid_email, email_result = validate_email_address(email)
        if not valid_email:
            return error_response(email_result, 400)
        
        # Use normalized email
        email = email_result
        
        # Validate password
        valid_password, password_msg = validate_password(password)
        if not valid_password:
            return error_response(password_msg, 400)
        
        # Register the user
        result, status_code = auth_service.register_user(username, email, password)
        
        # Log the JWT secret key
        current_app.logger.info(f"Registration using JWT_SECRET_KEY: {current_app.config['JWT_SECRET_KEY']}")
        
        return format_response(result, status_code)
    except Exception as e:
        current_app.logger.error(f"Error in register: {str(e)}")
        return error_response("Internal server error", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    try:
        data = request.json
        
        if not data:
            return error_response("No input data provided", 400)
        
        # Extract input fields
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')
        
        # Log the JWT secret key
        current_app.logger.info(f"Login using JWT_SECRET_KEY: {current_app.config['JWT_SECRET_KEY']}")
        
        if not username_or_email:
            return error_response("Username or email is required", 400)
        
        if not password:
            return error_response("Password is required", 400)
        
        # Add more detailed logging
        current_app.logger.info(f"Login attempt for: {username_or_email}")
        
        try:
            # Login the user
            result, status_code = auth_service.login_user(username_or_email, password)
            
            # Log access token details if login successful
            if status_code == 200 and 'access_token' in result:
                access_token = result['access_token']
                current_app.logger.info(f"Generated access token: {access_token[:20]}...")
            
            return format_response(result, status_code)
        except Exception as inner_e:
            current_app.logger.error(f"Login processing error: {str(inner_e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return error_response(f"Login processing error: {str(inner_e)}", 500)
            
    except Exception as e:
        current_app.logger.error(f"Error in login: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return error_response(f"Internal server error: {str(e)}", 500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        
        # Log the JWT secret key
        current_app.logger.info(f"Token refresh using JWT_SECRET_KEY: {current_app.config['JWT_SECRET_KEY']}")
        
        access_token = create_access_token(identity=current_user_id)
        
        # Log new token details
        current_app.logger.info(f"New access token generated: {access_token[:20]}...")
        
        return format_response({
            'message': 'Token refreshed successfully',
            'access_token': access_token
        }, 200)
    except Exception as e:
        current_app.logger.error(f"Error in refresh: {str(e)}")
        return error_response("Internal server error", 500)

# Add a debug endpoint to create a test token
@auth_bp.route('/debug/token', methods=['GET'])
def debug_token():
    """Create a test token for debugging"""
    try:
        # Create a token with user ID 1
        access_token = create_access_token(identity=1)
        
        # Log token details
        current_app.logger.info(f"Debug token created using JWT_SECRET_KEY: {current_app.config['JWT_SECRET_KEY']}")
        current_app.logger.info(f"Debug token: {access_token[:20]}...")
        
        return format_response({
            'message': 'Debug token created',
            'access_token': access_token,
            'jwt_secret_used': current_app.config['JWT_SECRET_KEY']
        }, 200)
    except Exception as e:
        current_app.logger.error(f"Error creating debug token: {str(e)}")
        return error_response("Internal server error", 500)