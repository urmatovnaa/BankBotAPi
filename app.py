import os
from dotenv import load_dotenv
load_dotenv()

import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


from database import db



# Set up logging
logging.basicConfig(level=logging.DEBUG)

os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///banking_chatbot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Initialize categories
    from supporting.categorization_service import question_categorizer
    question_categorizer.initialize_categories()

# Import and register routes
from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
