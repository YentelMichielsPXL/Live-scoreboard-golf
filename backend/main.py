from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from routers import players, tournaments, courses, auth, scores
import models
import hashlib

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(tournaments.router, prefix="/api")
app.include_router(players.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(scores.router, prefix="/api")
