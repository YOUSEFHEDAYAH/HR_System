"""
Reset Database Script
=====================
⚠️ WARNING: This script will DROP ALL TABLES and DELETE ALL DATA!

Use this script to completely reset the database schema.
Useful for development but NEVER use in production.

Usage:
    python scripts/reset_database.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.config import DatabaseConfig, DatabaseManager
from sqlalchemy import text


def reset_database():
    """Reset database by dropping and recreating all tables."""
    print("=" * 60)
    print("⚠️  DATABASE RESET TOOL")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print()
    
    # Ask for confirmation
    confirm = input("Are you sure you want to continue? Type 'YES' to confirm: ").strip()
    
    if confirm != 'YES':
        print("❌ Operation cancelled.")
        return False
    
    print()
    
    # Database configuration
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    # Initialize connection
    print("📡 Connecting to database...")
    if not db_manager.initialize(echo=False):
        print("❌ Failed to connect to database!")
        return False
    
    print()
    print("=" * 60)
    print("🗑️  Step 1: Dropping all existing tables...")
    print("=" * 60)
    
    # Get a session
    session = db_manager.get_session()
    
    try:
        # Drop tables manually in correct order
        print("   Dropping employee_chat_links...")
        session.execute(text("DROP TABLE IF EXISTS employee_chat_links CASCADE;"))
        
        print("   Dropping leave_requests...")
        session.execute(text("DROP TABLE IF EXISTS leave_requests CASCADE;"))
        
        print("   Dropping leave_balances...")
        session.execute(text("DROP TABLE IF EXISTS leave_balances CASCADE;"))
        
        print("   Dropping salaries...")
        session.execute(text("DROP TABLE IF EXISTS salaries CASCADE;"))
        
        print("   Dropping employees...")
        session.execute(text("DROP TABLE IF EXISTS employees CASCADE;"))
        
        print("   Dropping departments...")
        session.execute(text("DROP TABLE IF EXISTS departments CASCADE;"))
        
        # Commit the changes
        session.commit()
        print("✅ All tables dropped successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Failed to drop tables: {e}")
        session.close()
        return False
    finally:
        session.close()
    
    print()
    print("=" * 60)
    print("🏗️  Step 2: Creating new tables...")
    print("=" * 60)
    
    # Create all tables with new schema
    if db_manager.create_all_tables():
        print()
        print("=" * 60)
        print("✅ DATABASE RESET COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Generate sample data:")
        print("     python scripts/generate_sample_data.py")
        print()
        print("  2. Start the bot:")
        print("     python src/bot.py")
        print()
        return True
    else:
        print("❌ Failed to create tables!")
        return False


if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
