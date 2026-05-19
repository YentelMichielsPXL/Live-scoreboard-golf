from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/scores", tags=["scores"])

@router.post("/player/{player_id}")
def enter_hole_score(player_id: int, score_in: schemas.ScoreInput, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Speler niet gevonden")
        
    # Zoek naar een eventueel al bestaande score voor deze hole en ronde
    db_score = db.query(models.Score).filter(
        models.Score.player_id == player_id, 
        models.Score.round_number == score_in.round_number,
        models.Score.hole_number == score_in.hole_number
    ).first()
    
    # SLIMME VERWIJDER LOGICA: Als strokes 0 of leeg is, verwijder de scorekaart-entry
    if score_in.strokes <= 0:
        if db_score:
            db.delete(db_score)
            db.commit()
        return {"message": f"Ronde {score_in.round_number} Hole {score_in.hole_number} succesvol gewist"}
    
    # Normaliter: Updaten of nieuw aanmaken
    if db_score:
        db_score.strokes = score_in.strokes
    else:
        db_score = models.Score(
            player_id=player_id, 
            round_number=score_in.round_number,
            hole_number=score_in.hole_number, 
            strokes=score_in.strokes
        )
        db.add(db_score)
        
    db.commit()
    return {"message": f"Ronde {score_in.round_number} Hole {score_in.hole_number} opgeslagen"}