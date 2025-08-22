from flask import Flask
from app.config import config
from app.db import db
from app.routes.user_routes import user_routes
from app.routes.transaction_routes import transaction_bp
from app.routes.return_bp import return_bp
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Register Blueprints (Routes)
app.register_blueprint(user_routes)
app.register_blueprint(transaction_bp)
app.register_blueprint(return_bp)

# Create Tables (Run once)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
   port = int(os.environ.get("PORT", 5000))
   app.run(debug=False, host="0.0.0.0", port=port)
    
