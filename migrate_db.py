# migrate_db.py
from sqlalchemy import text
from db import engine, SessionLocal
from models import Base

def migrate_database():
    """
    Migrate the existing database to support the new webhook payload format.
    This script adds new columns while preserving existing data.
    """
    
    with engine.connect() as connection:
        # Start a transaction
        trans = connection.begin()
        
        try:
            print("Starting database migration...")
            
            # Add new columns to the existing Leads table
            migration_queries = [
                # Webhook metadata columns
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS event_id VARCHAR(255)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(100)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS provider VARCHAR(50)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS event_type VARCHAR(50)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS occurred_at TIMESTAMP',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS payload_version INTEGER DEFAULT 1',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS source_ids JSON',
                
                # Additional lead information columns
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS first_name VARCHAR(255)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS last_name VARCHAR(255)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP',
                
                # Consent columns
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS marketing_consent BOOLEAN',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS terms_consent BOOLEAN',
                
                # UTM tracking columns
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS utm_source VARCHAR(255)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS utm_medium VARCHAR(255)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS utm_campaign VARCHAR(255)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS utm_term VARCHAR(255)',
                'ALTER TABLE "Leads" ADD COLUMN IF NOT EXISTS utm_content VARCHAR(255)',
                
                # Make source column nullable for new records
                'ALTER TABLE "Leads" ALTER COLUMN source DROP NOT NULL',
            ]
            
            for query in migration_queries:
                print(f"Executing: {query}")
                connection.execute(text(query))
            
            # Update existing records with default values
            print("Updating existing records with default values...")
            
            update_queries = [
                # Populate provider from source for existing records
                'UPDATE "Leads" SET provider = source WHERE provider IS NULL',
                'UPDATE "Leads" SET event_type = \'lead.submitted\' WHERE event_type IS NULL',
                'UPDATE "Leads" SET occurred_at = created_on WHERE occurred_at IS NULL',
                'UPDATE "Leads" SET submitted_at = created_on WHERE submitted_at IS NULL',
                'UPDATE "Leads" SET payload_version = 0 WHERE payload_version IS NULL',  # Mark as legacy
            ]
            
            for query in update_queries:
                print(f"Executing: {query}")
                connection.execute(text(query))
            
            # Generate event_ids for existing records that don't have them
            print("Generating event_ids for existing records...")
            connection.execute(text('''
                UPDATE "Leads" 
                SET event_id = 'legacy-' || id::text 
                WHERE event_id IS NULL
            '''))
            
            # Add constraints after data migration
            print("Adding constraints...")
            constraint_queries = [
                'ALTER TABLE "Leads" ALTER COLUMN event_id SET NOT NULL',
                'ALTER TABLE "Leads" ADD CONSTRAINT unique_event_id UNIQUE (event_id)',
            ]
            
            for query in constraint_queries:
                try:
                    print(f"Executing: {query}")
                    connection.execute(text(query))
                except Exception as e:
                    print(f"Warning: Could not add constraint - {e}")
            
            # Commit the transaction
            trans.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate_database()
