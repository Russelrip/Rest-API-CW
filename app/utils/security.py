from functools import wraps
from flask import request, jsonify, current_app
from app.services.auth_service import auth_service
from app.models.api_usage import APIUsage
from app.database import db
import time

def require_api_key(f):
    """Decorator to require valid API key for access to protected endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = time.time()
        
        # Get API key from header or query parameter
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'error': 'API key is required',
                'message': 'Please provide an API key via X-API-Key header or api_key query parameter'
            }), 401
        
        # Validate the API key
        key, response, status_code = auth_service.validate_api_key(api_key)
        
        if status_code != 200:
            return jsonify(response), status_code
        
        # Calculate response time
        response_time = int((time.time() - start_time) * 1000)
        
        # If we reach here, the API key is valid
        try:
            # Record API usage
            usage = APIUsage(
                api_key_id=key.id,
                endpoint=request.path,
                method=request.method,
                status_code=200,  # Will be updated on completion
                response_time_ms=response_time,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string if request.user_agent else None
            )
            
            db.session.add(usage)
            db.session.commit()
            
            # Store API key and usage info for potential updates later
            request.api_key = key
            request.api_usage = usage
            
            # Proceed with the original function
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Error in API key middleware: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': 'An error occurred while processing your request'
            }), 500
    
    return decorated

def update_api_usage(status_code):
    """Update API usage record with the final status code"""
    try:
        if hasattr(request, 'api_usage'):
            request.api_usage.status_code = status_code
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error updating API usage: {str(e)}")