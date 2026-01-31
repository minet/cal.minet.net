import colorsys
import os

from sqlalchemy import create_engine, text


# Default to the one in database.py, but allow env override
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/calendint")


def hue_chroma_lightness_to_hex(h, c, l):
    """
    Converts HSL/HCL values to a Hexadecimal string.
    :param h: Hue (0-360)
    :param c: Chroma/Saturation (0-100)
    :param l: Lightness (0-100)
    :return: Hex string (e.g., #FFFFFF)
    """
    # 1. Normalize values to 0.0 - 1.0 range for colorsys
    h_norm = h / 360.0
    l_norm = l / 100.0
    s_norm = c / 100.0

    # 2. Convert HLS (Hue, Lightness, Saturation) to RGB
    # Note: colorsys uses HLS order
    r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)

    # 3. Scale back to 0-255 and convert to Hex
    return "#{:02x}{:02x}{:02x}".format(
        round(r * 255), 
        round(g * 255), 
        round(b * 255)
    ).upper()    
    

def run_migration():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            
            # Check if columns allow nulls or defaults - we will add them as nullable first
            print("Adding new color columns...")
            conn.execute(text("ALTER TABLE organization ADD COLUMN IF NOT EXISTS color_primary VARCHAR"))
            conn.execute(text("ALTER TABLE organization ADD COLUMN IF NOT EXISTS color_secondary VARCHAR"))
            conn.execute(text("ALTER TABLE organization ADD COLUMN IF NOT EXISTS color_dark VARCHAR"))
            
            check_chroma = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='organization' AND column_name='color_chroma'")).fetchone()
            check_hue = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='organization' AND column_name='color_hue'")).fetchone()

            # Convert old color_chroma and color_hue to new color columns
            # Query the old columns and update the new ones
            if check_chroma and check_hue:
                print("Converting old color columns to new color columns...")
                query = text("SELECT id, color_chroma, color_hue FROM organization WHERE color_chroma IS NOT NULL AND color_hue IS NOT NULL")
                result = conn.execute(query)
                for row in result:
                    org_id = row[0]
                    color_chroma = row[1]
                    color_hue = row[2]
                    
                    color_primary = hue_chroma_lightness_to_hex(color_hue, color_chroma, 50)
                    color_secondary = hue_chroma_lightness_to_hex(color_hue, color_chroma/2, 99)
                    color_dark = hue_chroma_lightness_to_hex(color_hue, color_chroma/2, 10)
                    
                    conn.execute(text("UPDATE organization SET color_primary = :color_primary, color_secondary = :color_secondary, color_dark = :color_dark WHERE id = :org_id"), {"color_primary": color_primary, "color_secondary": color_secondary, "color_dark": color_dark, "org_id": org_id})
            
            print("Removing old color columns...")
            # We check if they exist before dropping to allow re-run safe
            if check_chroma:
                conn.execute(text("ALTER TABLE organization DROP COLUMN color_chroma"))
            
            if check_hue:
                conn.execute(text("ALTER TABLE organization DROP COLUMN color_hue"))
                
            print("Migration successful.")
                
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
