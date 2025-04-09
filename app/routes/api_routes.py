from flask import Blueprint, request, jsonify, current_app
from app.services.countries_service import countries_service
from app.utils.security import require_api_key, update_api_usage
from app.utils.helpers import paginate_results, error_response, format_response
from app.utils.validators import sanitize_string

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/countries', methods=['GET'])
@require_api_key
def get_all_countries():
    """Get all countries with filtered data"""
    try:
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get countries data
        countries = countries_service.get_all_countries()
        
        # Check for errors in the response
        if 'error' in countries:
            update_api_usage(500)
            return error_response(countries['error'], 500)
        
        # Paginate results
        result = paginate_results(countries, page, per_page)
        
        # Update API usage record with successful status
        update_api_usage(200)
        
        return format_response(result, 200)
    except Exception as e:
        current_app.logger.error(f"Error in get_all_countries: {str(e)}")
        update_api_usage(500)
        return error_response("Internal server error", 500)

@api_bp.route('/countries/<name>', methods=['GET'])
@require_api_key
def get_country_by_name(name):
    """Get country by name"""
    try:
        # Sanitize input
        name = sanitize_string(name)
        
        # Get country data
        country = countries_service.get_country_by_name(name)
        
        # Check for errors in the response
        if 'error' in country:
            update_api_usage(404)
            return error_response(country['error'], 404)
        
        # Update API usage record with successful status
        update_api_usage(200)
        
        return format_response(country, 200)
    except Exception as e:
        current_app.logger.error(f"Error in get_country_by_name: {str(e)}")
        update_api_usage(500)
        return error_response("Internal server error", 500)

@api_bp.route('/countries/currency/<code>', methods=['GET'])
@require_api_key
def get_countries_by_currency(code):
    """Get countries by currency code"""
    try:
        # Sanitize input
        code = sanitize_string(code)
        
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get countries data
        countries = countries_service.get_countries_by_currency(code)
        
        # Check for errors in the response
        if 'error' in countries:
            update_api_usage(404)
            return error_response(countries['error'], 404)
        
        # Paginate results
        result = paginate_results(countries, page, per_page)
        
        # Update API usage record with successful status
        update_api_usage(200)
        
        return format_response(result, 200)
    except Exception as e:
        current_app.logger.error(f"Error in get_countries_by_currency: {str(e)}")
        update_api_usage(500)
        return error_response("Internal server error", 500)

@api_bp.route('/countries/language/<code>', methods=['GET'])
@require_api_key
def get_countries_by_language(code):
    """Get countries by language code"""
    try:
        # Sanitize input
        code = sanitize_string(code)
        
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get countries data
        countries = countries_service.get_countries_by_language(code)
        
        # Check for errors in the response
        if 'error' in countries:
            update_api_usage(404)
            return error_response(countries['error'], 404)
        
        # Paginate results
        result = paginate_results(countries, page, per_page)
        
        # Update API usage record with successful status
        update_api_usage(200)
        
        return format_response(result, 200)
    except Exception as e:
        current_app.logger.error(f"Error in get_countries_by_language: {str(e)}")
        update_api_usage(500)
        return error_response("Internal server error", 500)

@api_bp.route('/countries/region/<region>', methods=['GET'])
@require_api_key
def get_countries_by_region(region):
    """Get countries by region"""
    try:
        # Sanitize input
        region = sanitize_string(region)
        
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get countries data
        countries = countries_service.get_countries_by_region(region)
        
        # Check for errors in the response
        if 'error' in countries:
            update_api_usage(404)
            return error_response(countries['error'], 404)
        
        # Paginate results
        result = paginate_results(countries, page, per_page)
        
        # Update API usage record with successful status
        update_api_usage(200)
        
        return format_response(result, 200)
    except Exception as e:
        current_app.logger.error(f"Error in get_countries_by_region: {str(e)}")
        update_api_usage(500)
        return error_response("Internal server error", 500)

# Add API documentation endpoint
@api_bp.route('/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    docs = {
        'name': 'Countries API',
        'version': '1.0',
        'description': 'API for accessing filtered country data from RestCountries.com',
        'endpoints': [
            {
                'path': '/api/v1/countries',
                'method': 'GET',
                'description': 'Get all countries with filtered data',
                'auth': 'API Key required',
                'params': {
                    'page': 'Page number (default: 1)',
                    'per_page': 'Items per page (default: 20, max: 100)'
                }
            },
            {
                'path': '/api/v1/countries/{name}',
                'method': 'GET',
                'description': 'Get country by name',
                'auth': 'API Key required'
            },
            {
                'path': '/api/v1/countries/currency/{code}',
                'method': 'GET',
                'description': 'Get countries by currency code',
                'auth': 'API Key required',
                'params': {
                    'page': 'Page number (default: 1)',
                    'per_page': 'Items per page (default: 20, max: 100)'
                }
            },
            {
                'path': '/api/v1/countries/language/{code}',
                'method': 'GET',
                'description': 'Get countries by language code',
                'auth': 'API Key required',
                'params': {
                    'page': 'Page number (default: 1)',
                    'per_page': 'Items per page (default: 20, max: 100)'
                }
            },
            {
                'path': '/api/v1/countries/region/{region}',
                'method': 'GET',
                'description': 'Get countries by region',
                'auth': 'API Key required',
                'params': {
                    'page': 'Page number (default: 1)',
                    'per_page': 'Items per page (default: 20, max: 100)'
                }
            }
        ]
    }
    
    return format_response(docs, 200)