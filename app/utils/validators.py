import re
from email_validator import validate_email, EmailNotValidError

def validate_username(username):
    """
    Validate username format
    - Must be 3-20 characters
    - Can only contain letters, numbers, underscores and hyphens
    - Cannot start or end with underscore or hyphen
    """
    if not username or not isinstance(username, str):
        return False, "Username is required"
    
    if not 3 <= len(username) <= 20:
        return False, "Username must be 3-20 characters"
    
    # Check allowed characters
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$', username):
        return False, "Username can only contain letters, numbers, underscores and hyphens, and cannot start or end with underscore or hyphen"
    
    return True, ""

def validate_email_address(email):
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    try:
        # Validate and normalize the email
        valid = validate_email(email)
        # Get the normalized form
        normalized_email = valid.email
        return True, normalized_email
    except EmailNotValidError as e:
        return False, str(e)

def validate_password(password):
    """
    Validate password strength
    - Must be at least 8 characters
    - Must contain at least one uppercase letter
    - Must contain at least one lowercase letter
    - Must contain at least one number
    - Must contain at least one special character
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    # Check for uppercase
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for number
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, ""

def sanitize_string(input_string):
    """Sanitize string input to prevent injection attacks"""
    if not input_string or not isinstance(input_string, str):
        return ""
    
    # Remove any HTML tags
    sanitized = re.sub(r'<[^>]*>', '', input_string)
    
    # Limit length to reasonable size
    return sanitized[:500]  # Limit to 500 characters