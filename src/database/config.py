"""
Database Configuration
=====================
Database connection configuration and management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """
    Database connection configuration.
    
    Manages database connection parameters and provides
    methods for creating connection URLs and engines.
    """
    
    def __init__(self, user=None, password=None, host=None, port=None, database=None):
        """
        Initialize database configuration.
        
        Args:
            user: Database username (defaults to env var DB_USER)
            password: Database password (defaults to env var DB_PASSWORD)
            host: Database host (defaults to env var DB_HOST)
            port: Database port (defaults to env var DB_PORT)
            database: Database name (defaults to env var DB_NAME)
        """
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or os.getenv('DB_PORT', '5432')
        self.database = database or os.getenv('DB_NAME', 'hr_db')
    
    def get_connection_url(self):
        """
        Create database connection URL.
        
        Returns:
            str: PostgreSQL connection URL with encoded password
        """
        encoded_password = quote_plus(self.password)
        return f'postgresql://{self.user}:{encoded_password}@{self.host}:{self.port}/{self.database}'
    
    def create_engine(self, echo=None):
        """
        Create SQLAlchemy engine.
        
        Args:
            echo: Whether to echo SQL queries (defaults to env var DB_ECHO)
            
        Returns:
            Engine: SQLAlchemy engine instance
        """
        if echo is None:
            echo = os.getenv('DB_ECHO', 'False').lower() == 'true'
        
        url = self.get_connection_url()
        return create_engine(url, echo=echo)


class DatabaseManager:
    """
    Database management class.
    
    Handles database initialization, table creation/deletion,
    and session management.
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        Initialize database manager.
        
        Args:
            config: DatabaseConfig instance
        """
        self.config = config
        self.engine = None
        self.Session = None
    
    def initialize(self, echo=False):
        """
        Initialize database connection.
        
        Args:
            echo: Whether to echo SQL queries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.engine = self.config.create_engine(echo=echo)
            self.Session = sessionmaker(bind=self.engine)
            print("✅ Database connection established successfully!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def create_all_tables(self):
        """
        Create all tables defined in models.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from .models import Base
            Base.metadata.create_all(self.engine)
            print("✅ All tables created successfully!")
            print("\nCreated tables:")
            for table in Base.metadata.tables.keys():
                print(f"  - {table}")
            return True
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            return False
    
    def drop_all_tables(self):
        """
        Drop all tables.
        
        ⚠️ WARNING: This will DELETE ALL DATA!
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from .models import Base
            Base.metadata.drop_all(self.engine)
            print("✅ All tables dropped successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to drop tables: {e}")
            return False
    
    def get_session(self):
        """
        Get a database session for operations.
        
        Returns:
            Session: SQLAlchemy session instance
            
        Raises:
            Exception: If database manager is not initialized
        """
        if self.Session:
            return self.Session()
        raise Exception("DatabaseManager must be initialized first using initialize()")
