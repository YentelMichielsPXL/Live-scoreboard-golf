import hashlib
from database import engine, Base, SessionLocal
import models
import os

USERNAME = os.getenv("SECRET_USERNAME")
PASSWORD = os.getenv("SECRET_PASSWORD")

def init_db():
    print("1. Initializing the database...")
    Base.metadata.create_all(bind=engine)

    print("2. Checking for existing admin user...")
    db = SessionLocal()
    try:
        admin_exists = db.query(models.User).filter(models.User.username == USERNAME).first()
        if not admin_exists:
            hashed_password = hashlib.sha256(PASSWORD.encode()).hexdigest()
            default_admin = models.User(
                username=USERNAME, 
                password_hash=hashed_password, 
                role="admin"
            )
            db.add(default_admin)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Finished")