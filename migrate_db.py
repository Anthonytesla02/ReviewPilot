#!/usr/bin/env python3
"""
Database migration script for AI automation features.
Run this to create new tables in the production database.
"""

import os
import sys
from app import app, db

def create_tables():
    """Create all database tables if they don't exist"""
    try:
        with app.app_context():
            # Import all models to ensure they're registered
            from models import (
                User, ReviewTemplate, Customer, Review, ReviewRequest,
                ReviewConversation, FollowUpSequence, Referral, 
                AutomationSettings, ReportGeneration
            )
            
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Check if any users exist
            user_count = User.query.count()
            print(f"✓ Found {user_count} users in database")
            
            # Create default automation settings for existing users
            existing_users = User.query.filter(~User.id.in_(
                db.session.query(AutomationSettings.user_id)
            )).all()
            
            for user in existing_users:
                settings = AutomationSettings(user_id=user.id)
                db.session.add(settings)
                print(f"✓ Created default automation settings for user: {user.username}")
            
            if existing_users:
                db.session.commit()
                print(f"✓ Updated {len(existing_users)} users with automation settings")
            
            print("✓ Migration completed successfully!")
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        db.session.rollback()
        return False
    
    return True

if __name__ == '__main__':
    success = create_tables()
    sys.exit(0 if success else 1)