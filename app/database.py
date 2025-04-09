from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

# Initialize SQLAlchemy for database management
db = SQLAlchemy()

# Initialize Flask-Migrate for database migrations
migrate = Migrate()

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()

def init_db(app):
    """Initialize database and related extensions with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()