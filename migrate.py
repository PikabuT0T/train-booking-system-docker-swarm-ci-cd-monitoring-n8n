from app import create_app
from app import db

app = create_app()

with app.app_context():
    print("Running DB migrations...")
    db.create_all()
    print("Migrations completed.")

