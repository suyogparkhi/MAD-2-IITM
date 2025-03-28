from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Add is_active column to services table if it doesn't exist
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE services ADD COLUMN is_active BOOLEAN DEFAULT 1'))
            conn.commit()
        print("Added is_active column to services table")
    except Exception as e:
        print(f"Error adding column: {e}") 