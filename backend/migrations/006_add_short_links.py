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
            
            # Check if table exists
            check_sql = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='shortlink';
            """)
            result = conn.execute(check_sql).fetchone()
            
            if not result:
                print("Creating shortlink table...")
                create_sql = text("""
                CREATE TABLE IF NOT EXISTS shortlink (
                    id VARCHAR PRIMARY KEY,
                    item_type VARCHAR NOT NULL,
                    action_type VARCHAR NOT NULL,
                    item_id UUID NOT NULL,
                    created_by_id UUID NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                    last_used_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                    FOREIGN KEY (created_by_id) REFERENCES "user" (id)
                );
                """)
                conn.execute(create_sql)
                print("Migration successful.")
            else:
                print("Table shortlink already exists.")
                
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
