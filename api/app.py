import sys
import os

# Add the parent directory to the Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from app import app

# Ensure database tables are created when needed
def ensure_tables():
    from app import db
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"Database initialization error: {e}")

# Create tables on import for Vercel
if os.environ.get("VERCEL_ENV"):
    ensure_tables()

# Export for Vercel
application = app