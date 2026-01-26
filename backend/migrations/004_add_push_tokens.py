
from sqlalchemy import create_engine, text
import os

# Default to the one in database.py, but allow env override
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/calendint")

def run_migration():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            
            # Check if column exists
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='user' AND column_name='notification_delay';
            """)
            result = conn.execute(check_sql).fetchone()
            
            if not result:
                print("Adding notification_delay column to user table...")
                alter_sql = text("ALTER TABLE \"user\" ADD COLUMN notification_delay INTEGER DEFAULT 15")
                conn.execute(alter_sql)
                print("Migration successful.")
            else:
                print("Column notification_delay already exists.")
                
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
