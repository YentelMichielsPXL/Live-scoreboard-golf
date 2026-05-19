from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from routers import players, tournaments, courses, auth, scores
import models
import hashlib

# Maak de tabellen aan in Postgres
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
db = SessionLocal()
try:
    admin_exists = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_exists:
        hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
        default_admin = models.User(
            username="admin", 
            password_hash=hashed_password, 
            role="admin"
        )
        db.add(default_admin)
        db.commit()
        print("====== SEEDER: Standaard admin aangemaakt! Gebruikersnaam: admin | Wachtwoord: admin123 ======")
finally:
    db.close()

# Koppel alle routers
app.include_router(auth.router)
app.include_router(tournaments.router)
app.include_router(players.router)
app.include_router(courses.router)
app.include_router(scores.router)
