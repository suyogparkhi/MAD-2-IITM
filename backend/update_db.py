from app import create_app, db
from models.models import Professional
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Add address column to professionals table if it doesn't exist
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE professionals ADD COLUMN address TEXT'))
            conn.commit()
        print("Added address column to professionals table")
    except Exception as e:
        print(f"Error adding column: {e}")
        
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE professionals ADD COLUMN pin_code VARCHAR(10)'))
            conn.commit()
        print("Added pin_code column to professionals table")
    except Exception as e:
        print(f"Error adding column: {e}")
        
    # Recreate the database
    # db.drop_all()
    # db.create_all()
    # print("Database recreated successfully") 