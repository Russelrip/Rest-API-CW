from flask import jsonify
import traceback
import datetime
import json

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)

def format_response(data, status_code=200):
    """Format API response consistently"""
    response = jsonify(data)
    response.status_code = status_code
    return response

def error_response(message, status_code=400):
    """Format error response consistently"""
    return format_response({
        'error': True,
        'message': message
    }, status_code)

def log_error(app, e):
    """Log exception details to Flask logger"""
    app.logger.error(f"Exception: {str(e)}")
    app.logger.error(traceback.format_exc())

def paginate_results(items, page=1, per_page=20):
    """
    Paginate a list of items
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        per_page: Number of items per page
    
    Returns:
        dict: Paginated response with metadata
    """
    # Ensure valid pagination parameters
    page = max(1, int(page))
    per_page = max(1, min(100, int(per_page)))  # Between 1 and 100
    
    # Calculate total items and pages
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page  # Ceiling division
    
    # Adjust page if out of bounds
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Slice the items for the current page
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    page_items = items[start_idx:end_idx]
    
    # Construct pagination metadata
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_previous': page > 1,
        'has_next': page < total_pages
    }
    
    return {
        'items': page_items,
        'pagination': pagination
    }