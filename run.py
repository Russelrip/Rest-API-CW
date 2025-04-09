import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask app instance
app = create_app(os.getenv('FLASK_ENV', 'dev'))

if __name__ == '__main__':
    # Run the app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=app.config['DEBUG'])