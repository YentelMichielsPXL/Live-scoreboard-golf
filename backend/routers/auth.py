from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import hashlib
import uuid
from typing import List, Literal
import models
import schemas
from database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    user = db.query(models.User).filter(models.User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Sessie verlopen of ongeldig")
    return user

@router.post("/login", response_model=schemas.UserResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    hashed = hash_password(credentials.password)
    user = db.query(models.User).filter(models.User.username == credentials.username, models.User.password_hash == hashed).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Gebruikersnaam of wachtwoord onjuist")
    
    user.token = str(uuid.uuid4())
    db.commit()
    return user

@router.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen gebruikers aanmaken")
        
    existing = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Gebruikersnaam bestaat al")
        
    new_user = models.User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/allUsers", response_model=List[schemas.UserResponse])
def get_all_users(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.User).all()

class RoleUpdateBody(BaseModel):
    new_role: Literal["admin", "scorer"]

@router.put("/updateRole/{user_id}")
def update_user_role(
    user_id: int, 
    role_data: RoleUpdateBody, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen gebruikersrollen aanpassen")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Gebruiker niet gevonden")
    
    user.role = role_data.new_role
    db.commit()
    return {"message": f"Rol van gebruiker {user.username} is bijgewerkt naar {user.role}",
            "new_role": user.role,
            "is_self": user.id == current_user.id}

# --- NIEUW: WACHTWOORD RESET ROUTE ---
class PasswordResetBody(BaseModel):
    password: str

@router.put("/reset-password/{user_id}")
def reset_password(
    user_id: int, 
    reset_data: PasswordResetBody, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen wachtwoorden resetten")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Gebruiker niet gevonden")
    
    # Versleutel het nieuwe wachtwoord en forceer de gebruiker om opnieuw in te loggen
    user.password_hash = hash_password(reset_data.password)
    user.token = None 
    db.commit()
    
    return {"message": f"Wachtwoord voor {user.username} is succesvol gewijzigd."}

@router.delete("/delete/{user_id}")
def delete_user(
    user_id: int, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen gebruikers verwijderen")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Gebruiker niet gevonden")
    
    db.delete(user)
    db.commit()
    return {"message": f"Gebruiker {user.username} is succesvol verwijderd"}