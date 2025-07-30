import os
from app import app

# For Vercel deployment
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:////tmp/reviews.db")

# This is the entry point for Vercel
if __name__ == "__main__":
    app.run()