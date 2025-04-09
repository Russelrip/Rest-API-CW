from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import auth_service
from app.utils.validators import sanitize_string
from app.utils.helpers import format_response, error_response

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/api-keys', methods=['GET'])
@jwt_required()
def get_api_keys():
    try:
        # Log current user identity
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"Retrieving API keys for user ID: {current_user_id}")
        
        # Log request headers for debugging
        auth_header = request.headers.get('Authorization', 'None')
        current_app.logger.info(f"Authorization header: {auth_header[:20]}...")
        current_app.logger.info(f"Request headers: {dict(request.headers)}")
        
        result, status_code = auth_service.get_user_api_keys(current_user_id)
        current_app.logger.info(f"API keys response: status {status_code}")
        return format_response(result, status_code)
    except Exception as e:
        current_app.logger.error(f"Error in get_api_keys: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return error_response(f"Internal server error: {str(e)}", 500)
    
@user_bp.route('/api-keys', methods=['POST'])
@jwt_required()
def create_api_key():
    """Create a new API key for the current user"""
    try:
        user_id = get_jwt_identity()
        current_app.logger.info(f"Creating API key for user ID: {user_id}")
        
        data = request.json or {}
        
        # Get optional parameters
        name = sanitize_string(data.get('name', ''))
        expires_in_days = data.get('expires_in_days', 365)
        
        # Validate expiration days
        try:
            expires_in_days = int(expires_in_days)
            if expires_in_days < 1 or expires_in_days > 3650:  # Max 10 years
                return error_response("Expiration days must be between 1 and 3650", 400)
        except (ValueError, TypeError):
            return error_response("Invalid expiration days", 400)
        
        result, status_code = auth_service.create_api_key(user_id, name, expires_in_days)
        current_app.logger.info(f"API key creation response: status {status_code}")
        
        return format_response(result, status_code)
    except Exception as e:
        current_app.logger.error(f"Error in create_api_key: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return error_response(f"Internal server error: {str(e)}", 500)

@user_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@jwt_required()
def revoke_api_key(key_id):
    """Revoke an API key"""
    try:
        user_id = get_jwt_identity()
        current_app.logger.info(f"Revoking API key {key_id} for user ID: {user_id}")
        
        result, status_code = auth_service.revoke_api_key(user_id, key_id)
        current_app.logger.info(f"API key revocation response: status {status_code}")
        
        return format_response(result, status_code)
    except Exception as e:
        current_app.logger.error(f"Error in revoke_api_key: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return error_response(f"Internal server error: {str(e)}", 500)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile information"""
    try:
        user_id = get_jwt_identity()
        current_app.logger.info(f"Getting profile for user ID: {user_id}")
        
        from app.models import User
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        return format_response({
            'user': user.to_dict()
        }, 200)
    except Exception as e:
        current_app.logger.error(f"Error in get_profile: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return error_response(f"Internal server error: {str(e)}", 500)