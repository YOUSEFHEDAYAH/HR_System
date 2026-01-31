"""
Database Setup Script
====================
Initialize database schema and create all tables.

Usage:
    python scripts/setup_database.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.config import DatabaseConfig, DatabaseManager

def setup_database():
    """Initialize database and create all tables."""
    print("=" * 60)
    print("🏗️  HR Database Setup")
    print("=" * 60)
    print()
    
    # Create database manager with environment configuration
    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    
    # Initialize connection
    print("📡 Connecting to database...")
    if not db_manager.initialize(echo=False):
        print("❌ Failed to connect to database!")
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Database credentials in .env file")
        print("  3. Database exists (createdb hr_db)")
        return False
    
    print()
    
    # Create all tables
    print("🏗️  Creating tables...")
    if not db_manager.create_all_tables():
        print("❌ Failed to create tables!")
        return False
    
    print()
    print("=" * 60)
    print("✅ Database setup completed successfully!")
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


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
