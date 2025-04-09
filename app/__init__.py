import os
import logging
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import config
from app.database import init_db
from app.utils.helpers import JSONEncoder

# Initialize JWT
jwt = JWTManager()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name='dev'):
    """Create and configure the Flask application"""
    # Create Flask app
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Load configuration
    app.config.from_object(config)
    
    # Handle environment variable mapping for FLASK_ENV
    if config_name == 'development':
        config_name = 'dev'
    
    # FIXED: Hardcode JWT secret key for now
    # This ensures consistent secret key usage
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-for-debugging-purposes'
    
    # Set up JWT configurations
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'
    
    # Set up logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info(f"App starting with JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")
    
    # Ensure COUNTRIES_API_URL is set
    if 'COUNTRIES_API_URL' not in app.config:
        app.config['COUNTRIES_API_URL'] = 'https://restcountries.com/v3.1'
    
    # Set custom JSON encoder
    app.json_encoder = JSONEncoder
    
    # Initialize database
    init_db(app)
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Add token generation endpoint
    @app.route('/generate-test-token')
    def generate_test_token():
        """Generate a test token for debugging"""
        # Use string for user ID to avoid type issues
        test_token = create_access_token(identity="test-user")
        return jsonify({
            "access_token": test_token,
            "message": "Test token generated with hardcoded secret",
            "secret_key": app.config['JWT_SECRET_KEY']
        })
    
    # Add debugging endpoint for JWT tokens
    @app.route('/debug-token')
    def debug_token():
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "No bearer token provided"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Try with our hardcoded key
        import jwt as pyjwt
        try:
            decoded = pyjwt.decode(
                token, 
                app.config['JWT_SECRET_KEY'],
                algorithms=["HS256"]
            )
            return jsonify({
                "success": True,
                "message": "Token verified successfully",
                "secret_key": app.config['JWT_SECRET_KEY'],
                "decoded": decoded
            })
        except Exception as e:
            return jsonify({
                "error": str(e),
                "message": "Token verification failed",
                "secret_key": app.config['JWT_SECRET_KEY'],
                "token_slice": token[:20] + "..."
            }), 401
    
    # Add test-simple-auth endpoint
    @app.route('/test-simple-auth')
    def test_simple_auth():
        """Test endpoint that manually decodes the JWT token"""
        import jwt
        
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "No bearer token"}), 401
            
        token = auth_header.split(' ')[1]
        jwt_secret = app.config['JWT_SECRET_KEY']
        
        try:
            # Try to decode the token manually
            decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            return jsonify({
                "success": True,
                "message": "Token manually verified",
                "secret_key_used": jwt_secret[:5] + "...",
                "decoded": decoded
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "jwt_secret_key": jwt_secret,
                "token_slice": token[:20] + "..."
            }), 401
    
    with app.app_context():
        # Import services and initialize them with the app
        from app.services.countries_service import countries_service
        from app.services.auth_service import auth_service
        
        # Initialize services with app
        countries_service.init_app(app)
        
        # Import and register blueprints
        from app.routes import register_blueprints
        register_blueprints(app)
    
    # Configure error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok', 
            'service': 'countries-api',
            'jwt_secret': app.config['JWT_SECRET_KEY'][:5] + '...'
        })
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        app.logger.warning(f"Expired token: {jwt_payload}")
        return jsonify({
            'message': 'The token has expired',
            'error': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        app.logger.warning(f"Invalid token: {error}")
        return jsonify({
            'message': 'Signature verification failed',
            'error': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        app.logger.warning(f"Missing token: {error}")
        return jsonify({
            'message': 'Request does not contain an access token',
            'error': 'authorization_required'
        }), 401
    
    return app