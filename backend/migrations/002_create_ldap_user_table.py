import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/calendint")

def run_migration():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            
            # Check if table exists
            check_sql = text("""
                SELECT to_regclass('public.ldapuser');
            """)
            result = conn.execute(check_sql).fetchone()
            
            if not result or not result[0]:
                print("Creating table ldapuser...")
                create_sql = text("""
                CREATE TABLE ldapuser (
                    id UUID NOT NULL, 
                    email VARCHAR NOT NULL, 
                    full_name VARCHAR, 
                    uid VARCHAR, 
                    synced_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
                    PRIMARY KEY (id)
                );
                CREATE UNIQUE INDEX ix_ldapuser_email ON ldapuser (email);
                CREATE INDEX ix_ldapuser_uid ON ldapuser (uid);
                """)
                conn.execute(create_sql)
                print("Migration successful.")
            else:
                print("Table ldapuser already exists.")
                
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
