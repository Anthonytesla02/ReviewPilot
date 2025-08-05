#!/usr/bin/env python3
"""
Add missing columns to existing tables in production database.
This script adds the AI automation columns to existing tables.
"""

import os
import psycopg2
from sqlalchemy import text

def add_missing_columns():
    """Add missing columns to existing tables"""
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("✗ DATABASE_URL not found in environment variables")
            return False
        
        print(f"Connecting to database...")
        
        # Import after environment is ready
        from app import app, db
        
        with app.app_context():
            # SQL commands to add missing columns
            migration_sql = [
                # Add new columns to customer table
                "ALTER TABLE customer ADD COLUMN IF NOT EXISTS total_services INTEGER DEFAULT 1;",
                "ALTER TABLE customer ADD COLUMN IF NOT EXISTS average_rating FLOAT;",
                "ALTER TABLE customer ADD COLUMN IF NOT EXISTS last_rating INTEGER;",
                "ALTER TABLE customer ADD COLUMN IF NOT EXISTS location VARCHAR(200);",
                "ALTER TABLE customer ADD COLUMN IF NOT EXISTS segment_tags TEXT;",
                
                # Add new columns to review table for AI features
                "ALTER TABLE review ADD COLUMN IF NOT EXISTS sentiment VARCHAR(50);",
                "ALTER TABLE review ADD COLUMN IF NOT EXISTS sentiment_score FLOAT;",
                "ALTER TABLE review ADD COLUMN IF NOT EXISTS ai_suggested_response TEXT;",
                "ALTER TABLE review ADD COLUMN IF NOT EXISTS voice_recording_path VARCHAR(500);",
                "ALTER TABLE review ADD COLUMN IF NOT EXISTS voice_transcription TEXT;",
                "ALTER TABLE review ADD COLUMN IF NOT EXISTS review_category VARCHAR(100);",
            ]
            
            print("Adding missing columns to existing tables...")
            
            for sql_command in migration_sql:
                try:
                    db.session.execute(text(sql_command))
                    print(f"✓ Executed: {sql_command.strip()}")
                except Exception as e:
                    print(f"⚠ Skipped: {sql_command.strip()} - {str(e)}")
            
            # Commit the column additions
            db.session.commit()
            print("✓ Column migration completed successfully!")
            
            # Now create the new tables
            print("Creating new AI automation tables...")
            db.create_all()
            print("✓ All tables created successfully!")
            
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False
    
    return True

if __name__ == '__main__':
    import sys
    success = add_missing_columns()
    sys.exit(0 if success else 1)