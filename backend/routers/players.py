from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
import csv
import io
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/tournaments/{tournament_id}/players",
    tags=["players"]
)

class PlayerStatusUpdate(BaseModel):
    status: str

@router.get("/", response_model=List[schemas.Player])
def get_tournament_players(tournament_id: int, db: Session = Depends(get_db)):
    return db.query(models.Player).filter(models.Player.tournament_id == tournament_id).all()

@router.post("/", response_model=schemas.Player)
def add_player_to_tournament(tournament_id: int, player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")
    
    db_player = models.Player(**player.model_dump(), tournament_id=tournament_id)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@router.put("/{player_id}/status")
def update_player_status(tournament_id: int, player_id: int, status_update: PlayerStatusUpdate, db: Session = Depends(get_db)):
    db_player = db.query(models.Player).filter(
        models.Player.id == player_id, 
        models.Player.tournament_id == tournament_id
    ).first()
    
    if not db_player:
        raise HTTPException(status_code=404, detail="Speler niet gevonden in dit toernooi")
    
    if status_update.status not in ["ACTIVE", "DQ", "WD", "CUT"]:
        raise HTTPException(status_code=400, detail="Ongeldige status.")
        
    db_player.status = status_update.status
    db.commit()
    return {"message": "Status succesvol geüpdatet", "status": db_player.status}

@router.post("/upload-csv")
async def upload_players_csv(tournament_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Bestand moet een .csv zijn")
    
    content = await file.read()
    decoded_content = content.decode('utf-8-sig')
    
    first_line = decoded_content.split('\n')[0]
    delimiter = ';' if ';' in first_line else ','
    
    csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=delimiter)
    detected_headers = csv_reader.fieldnames
    
    players_added = 0
    for row in csv_reader:
        try:
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            
            if not first_name:
                first_name = row.get('First_name', row.get('FIRST_NAME', '')).strip()
            if not last_name:
                last_name = row.get('Last_name', row.get('LAST_NAME', '')).strip()

            if not first_name or not last_name:
                continue
            
            gender_str = row.get('gender', row.get('GENDER', 'M')).strip().upper()
            if gender_str == 'V':
                gender_str = 'F'
            if gender_str not in ['M', 'F']:
                gender_str = 'M'

            handicap_str = row.get('handicap', row.get('HANDICAP', '')).strip().replace(',', '.')
            handicap_val = float(handicap_str) if handicap_str else None
            
            db_player = models.Player(
                first_name=first_name,
                last_name=last_name,
                handicap=handicap_val,
                tournament_id=tournament_id,
                status="ACTIVE",
                gender=gender_str
            )
            db.add(db_player)
            players_added += 1
        except Exception:
            continue

    if players_added == 0:
        raise HTTPException(
            status_code=400, 
            detail=f"0 spelers geïmporteerd. Gevonden kolommen: {detected_headers}. Zorg voor 'first_name', 'last_name', 'handicap' (en optioneel 'gender')."
        )

    db.commit()
    return {"message": f"{players_added} spelers succesvol aan dit toernooi toegevoegd!"}

@router.delete("/{player_id}")
def delete_player_from_tournament(tournament_id: int, player_id: int, db: Session = Depends(get_db)):
    db_player = db.query(models.Player).filter(
        models.Player.id == player_id, 
        models.Player.tournament_id == tournament_id
    ).first()
    
    if not db_player:
        raise HTTPException(status_code=404, detail="Speler niet gevonden in dit toernooi")
        
    db.delete(db_player)
    db.commit()
    return {"message": "Speler succesvol verwijderd uit het toernooi"}