# init_db.py
from sqlalchemy import inspect
from db import Base, engine
from models import Lead

def init_database():
    """Initialize database tables"""
    
    # Check if tables already exist
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if "Leads" in existing_tables:
        print("Leads table already exists.")
        print("If you need to migrate to the new schema, run: python migrate_db.py")
    else:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    
    print("Database initialization complete.")

if __name__ == "__main__":
    init_database()
