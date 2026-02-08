#!/usr/bin/env python3
"""
Database initialization script for Curio Decision Record application.

This script creates the PostgreSQL database and initializes all required tables.
Run this script after setting up PostgreSQL to prepare the database for the application.
"""

import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from database_service import DatabaseService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_database():
    """Create the database if it doesn't exist."""
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '5432'))
    database = os.getenv('DB_NAME', 'curio_decision_record')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'postgres')
    
    try:
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=host,
            port=port,
            database='postgres',  # Connect to default postgres database
            user=user,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
            exists = cursor.fetchone()
            
            if not exists:
                # Create database
                cursor.execute(f'CREATE DATABASE "{database}"')
                logger.info(f"Database '{database}' created successfully")
            else:
                logger.info(f"Database '{database}' already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False


def initialize_tables():
    """Initialize all database tables."""
    try:
        db_service = DatabaseService()
        
        # Test connection
        if not db_service.test_connection():
            logger.error("Failed to connect to database")
            return False
        
        # Create tables using SQL files
        db_service.create_tables()
        logger.info("All tables created successfully from SQL files")
        
        db_service.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize tables: {e}")
        return False


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python init_db.py [create|init|reset]")
        print("  create - Create the database")
        print("  init   - Initialize tables (assumes database exists)")
        print("  reset  - Drop and recreate all tables")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        success = create_database()
    elif command == 'init':
        success = initialize_tables()
    elif command == 'reset':
        logger.info("Resetting database...")
        try:
            db_service = DatabaseService()
            
            # Test connection
            if not db_service.test_connection():
                logger.error("Failed to connect to database")
                success = False
            else:
                # Drop all tables first
                db_service.drop_tables()
                # Then recreate them
                db_service.create_tables()
                logger.info("Database reset completed successfully")
                success = True
            
            db_service.close()
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            success = False
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, init, reset")
        sys.exit(1)
    
    if success:
        logger.info("Operation completed successfully")
        sys.exit(0)
    else:
        logger.error("Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
