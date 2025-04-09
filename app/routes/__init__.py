from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.api_routes import api_bp
from app.routes.web_routes import web_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)