from datetime import datetime
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User, APIKey
from app.database import db
import re
import uuid

class AuthService:
    """Service for handling user authentication and API key management"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
    
    def register_user(self, username, email, password):
        """Register a new user"""
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            return {'error': 'Username already exists'}, 400
        
        if User.query.filter_by(email=email).first():
            return {'error': 'Email already registered'}, 400
        
        # Validate password strength
        if not self._validate_password(password):
            return {'error': 'Password must be at least 8 characters and include uppercase, lowercase, number, and special character'}, 400
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                password=password
            )
            db.session.add(user)
            db.session.commit()
            
            # Generate tokens
            tokens = self._generate_tokens(user)
            
            return {
                'message': 'User registered successfully',
                'user': user.to_dict(),
                **tokens
            }, 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error registering user: {str(e)}")
            return {'error': 'Failed to register user'}, 500
    
    def login_user(self, username_or_email, password):
        """Authenticate a user and generate tokens"""
        # Find user by username or email
        user = User.query.filter((User.username == username_or_email) | 
                                (User.email == username_or_email)).first()
        
        if not user or not user.check_password(password):
            return {'error': 'Invalid credentials'}, 401
        
        # Update last login timestamp
        user.update_last_login()
        
        # Generate tokens
        tokens = self._generate_tokens(user)
        
        # Log token info
        if 'access_token' in tokens:
            current_app.logger.info(f"Generated access token for user {user.id}: {tokens['access_token'][:20]}...")
        
        return {
            'message': 'Login successful',
            'user': user.to_dict(),
            **tokens
        }, 200
    
    def create_api_key(self, user_id, name=None, expires_in_days=365):
        """Create a new API key for a user"""
        try:
            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            # Create new API key
            api_key = APIKey(
                user_id=user_id,
                name=name,
                expires_in_days=expires_in_days
            )
            
            db.session.add(api_key)
            db.session.commit()
            
            # Return the full API key information (including the key value)
            # This is the only time the key value will be returned
            return {
                'message': 'API key created successfully',
                'api_key': api_key.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating API key: {str(e)}")
            return {'error': 'Failed to create API key'}, 500
    
    def get_user_api_keys(self, user_id):
        """Get all API keys for a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            # Return list of API keys (without key values)
            api_keys = [key.to_safe_dict() for key in user.api_keys]
            
            return {
                'api_keys': api_keys
            }, 200
        except Exception as e:
            current_app.logger.error(f"Error retrieving API keys: {str(e)}")
            return {'error': 'Failed to retrieve API keys'}, 500
    
    def revoke_api_key(self, user_id, key_id):
        """Revoke an API key"""
        try:
            # Get the API key
            api_key = APIKey.query.get(key_id)
            
            if not api_key:
                return {'error': 'API key not found'}, 404
            
            if api_key.user_id != user_id:
                return {'error': 'Unauthorized'}, 403
            
            # Revoke the key
            api_key.revoke()
            
            return {
                'message': 'API key revoked successfully'
            }, 200
        except Exception as e:
            current_app.logger.error(f"Error revoking API key: {str(e)}")
            return {'error': 'Failed to revoke API key'}, 500
    
    def validate_api_key(self, api_key_value):
        """Validate an API key and return the associated user"""
        try:
            # Find API key by value
            api_keys = APIKey.query.all()
            found_key = None
            
            for key in api_keys:
                if key.check_key(api_key_value):
                    found_key = key
                    break
                    
            if not found_key:
                return None, {'error': 'Invalid API key'}, 401
            
            # Check if key is active and not expired
            if not found_key.is_valid():
                return None, {'error': 'API key is expired or inactive'}, 401
            
            # Log usage
            found_key.log_usage()
            
            # Return the user associated with this key
            user = User.query.get(found_key.user_id)
            
            return found_key, {'user': user.to_dict()}, 200
        except Exception as e:
            current_app.logger.error(f"Error validating API key: {str(e)}")
            return None, {'error': 'Failed to validate API key'}, 500
    
    def _generate_tokens(self, user):
        """Generate access and refresh tokens for a user"""
        try:
            # Convert user ID to string to avoid type issues
            user_id_str = str(user.id)
            
            # Log the JWT secret key being used
            current_app.logger.info(f"Generating tokens with JWT_SECRET_KEY: {current_app.config['JWT_SECRET_KEY']}")
            
            access_token = create_access_token(identity=user_id_str)
            refresh_token = create_refresh_token(identity=user_id_str)
            
            # Log successful token generation
            current_app.logger.info(f"Generated tokens for user ID: {user_id_str}")
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except Exception as e:
            current_app.logger.error(f"Error generating tokens: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return {'error': 'Failed to generate authentication tokens'}
    
    def _validate_password(self, password):
        """Validate password strength"""
        # At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
        if len(password) < 8:
            return False
            
        patterns = [
            r'[A-Z]',  # Uppercase
            r'[a-z]',  # Lowercase
            r'[0-9]',  # Number
            r'[!@#$%^&*(),.?":{}|<>]'  # Special character
        ]
        
        return all(re.search(pattern, password) for pattern in patterns)

# Initialize the auth service
auth_service = AuthService()