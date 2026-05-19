import math
from datetime import datetime
from typing import List
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
import models
from pydantic import BaseModel
from routers.auth import get_current_user
import schemas
from sqlalchemy.orm import Session

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


# Invoer-modellen voor de JSON bodies
class StatusUpdateBody(BaseModel):
    status: str


class CutUpdateBody(BaseModel):
    cut_percentage: int
    has_cut: bool


class TournamentCreateBody(BaseModel):
    name: str
    date: str
    course_id: int
    format: str
    has_cut: bool
    cut_percentage: int
    num_rounds: int


# Echte golf-afronding (voorkomt Python's bankers-rounding bug)
def golf_round(value: float) -> int:
    if value >= 0:
        return int(value + 0.5)
    else:
        return int(value - 0.5)


# =================================================================
# 1. STATISCHE EN FIXED ROUTES
# =================================================================


@router.get("/")
def get_tournaments(db: Session = Depends(get_db)):
    """Haal alle toernooien op, inclusief automatische 'is_active' berekening."""
    tournaments = db.query(models.Tournament).order_by(models.Tournament.id.desc()).all()
    results = []
    
    for t in tournaments:
        players = db.query(models.Player).filter(models.Player.tournament_id == t.id).all()
        
        # AUTOMATISCHE STATUS BEREKENING
        is_active = True
        if players:
            all_done = True
            for p in players:
                if p.status in ["WD", "DQ", "CUT"]:
                    continue
                
                valid_scores = sum(1 for s in p.scores if s.strokes > 0)
                if valid_scores < (18 * t.num_rounds):
                    all_done = False
                    break
            
            if all_done:
                is_active = False

        results.append({
            "id": t.id,
            "name": t.name,
            "date": str(t.date) if t.date else None,
            "format": t.format,
            "num_rounds": t.num_rounds,
            "has_cut": t.has_cut,
            "cut_percentage": t.cut_percentage,
            "is_active": is_active,
            "course": {"name": t.course.name} if hasattr(t, "course") and t.course else None,
            "players": [p.id for p in players]
        })
        
    return results


@router.get("/active/metadata")
def get_active_tournament_metadata(db: Session = Depends(get_db)):
    """Haal de instellingen van het meest recente/actieve toernooi op."""
    t = (
        db.query(models.Tournament)
        .order_by(models.Tournament.id.desc())
        .first()
    )
    if not t:
        raise HTTPException(
            status_code=404, detail="Er zijn nog geen toernooien aangemaakt"
        )
    return {
        "id": t.id,
        "name": t.name,
        "format": t.format,
        "num_rounds": t.num_rounds,
        "has_cut": t.has_cut,
        "cut_percentage": t.cut_percentage,
    }


@router.get("/active/leaderboard")
def get_active_leaderboard(db: Session = Depends(get_db)):
    """Haal het leaderboard van het allernieuwste/actieve toernooi op."""
    t = (
        db.query(models.Tournament)
        .order_by(models.Tournament.id.desc())
        .first()
    )
    if not t:
        raise HTTPException(
            status_code=404, detail="Geen actief toernooi gevonden"
        )

    return get_tournament_leaderboard(t.id, db)


@router.post("/")
def create_tournament(
    body: TournamentCreateBody,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Maak een nieuw toernooi aan (Alleen voor Admins)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen toernooien aanmaken")
    
    try:
        parsed_date = datetime.strptime(body.date, "%Y-%m-%d").date()
    except Exception:
        parsed_date = body.date

    new_tournament = models.Tournament(
        name=body.name,
        date=parsed_date,
        course_id=body.course_id,
        format=body.format,
        has_cut=body.has_cut,
        cut_percentage=body.cut_percentage,
        num_rounds=body.num_rounds
    )
    db.add(new_tournament)
    db.commit()
    db.refresh(new_tournament)
    return {"message": "Toernooi succesvol aangemaakt", "id": new_tournament.id}


# =================================================================
# 2. SUB-PADEN
# =================================================================


@router.put("/players/{player_id}/status")
def change_player_status(
    player_id: int,
    body: StatusUpdateBody,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Wijzig de status van een speler (ACTIVE, WD, DQ, CUT)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Alleen admins mogen spelersstatussen wijzigen",
        )

    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Speler niet gevonden")

    player.status = body.status
    db.commit()
    return {"message": f"Status succesvol gewijzigd naar {body.status}"}


# =================================================================
# 3. DYNAMISCHE TOERNOOI-ID ROUTES
# =================================================================


@router.get("/{tournament_id}/players")
def get_tournament_players(tournament_id: int, db: Session = Depends(get_db)):
    """Haal de pure spelerlijst op voor het Admin-beheer (PlayersAdmin.vue)."""
    players = (
        db.query(models.Player)
        .filter(models.Player.tournament_id == tournament_id)
        .all()
    )
    return [
        {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "handicap": p.handicap,
            "status": p.status,
            "scores": [
                {
                    "round_number": s.round_number,
                    "hole_number": s.hole_number,
                    "strokes": s.strokes,
                }
                for s in p.scores
            ],
        }
        for p in players
    ]


@router.get("/{tournament_id}/leaderboard")
def get_tournament_leaderboard(
    tournament_id: int, db: Session = Depends(get_db)
):
    """Haal het complete geformatteerde scorebord op inclusief de nieuwe THRU tie-breaker logica."""
    t = (
        db.query(models.Tournament)
        .filter(models.Tournament.id == tournament_id)
        .first()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")

    # Holes inladen
    holes_data = []
    if hasattr(t, "course") and t.course and hasattr(t.course, "holes"):
        for h in sorted(t.course.holes, key=lambda x: x.hole_number):
            holes_data.append({
                "hole_number": h.hole_number,
                "par": h.par,
                "stroke_index": h.stroke_index
            })
    elif hasattr(t, "course_id") and t.course_id:
        try:
            holes = db.query(models.Hole).filter(models.Hole.course_id == t.course_id).order_by(models.Hole.hole_number).all()
            for h in holes:
                holes_data.append({
                    "hole_number": h.hole_number,
                    "par": h.par,
                    "stroke_index": h.stroke_index
                })
        except Exception:
            pass

    if not holes_data:
        holes_data = [{"hole_number": i, "par": 4, "stroke_index": i} for i in range(1, 19)]

    total_par = sum([h["par"] for h in holes_data])

    # Haal WHS ratings op
    course_slope = 113
    course_cr = total_par
    if t.course:
        course_slope = getattr(t.course, "slope_rating", getattr(t.course, "slope", 113))
        course_cr = getattr(t.course, "course_rating", getattr(t.course, "cr", total_par))

    players = (
        db.query(models.Player)
        .filter(models.Player.tournament_id == tournament_id)
        .all()
    )

    players_with_calculations = []
    for p in players:
        total_strokes = sum([s.strokes for s in p.scores if s.strokes > 0])
        exact_hcp = p.handicap if p.handicap is not None else 0.0
        
        raw_playing_hcp = exact_hcp * (course_slope / 113.0) + (course_cr - total_par)
        playing_hcp = golf_round(raw_playing_hcp)
        
        total_to_par = 0
        total_stableford = 0
        has_played_any = False
        holes_played = 0 # Houdt het totaal aantal ingevulde gaten bij
        
        for s in p.scores:
            if s.strokes > 0:
                has_played_any = True
                holes_played += 1
                hole_meta = next((h for h in holes_data if h["hole_number"] == s.hole_number), None)
                par = hole_meta["par"] if hole_meta else 4
                si = hole_meta["stroke_index"] if hole_meta else s.hole_number
                
                total_to_par += (s.strokes - par)
                
                if playing_hcp >= 0:
                    base_extra = playing_hcp // 18
                    remainder = playing_hcp % 18
                    extra_strokes = base_extra + (1 if si <= remainder else 0)
                else:
                    abs_hcp = abs(playing_hcp)
                    base_giveback = abs_hcp // 18
                    remainder_giveback = abs_hcp % 18
                    extra_strokes = -base_giveback - (1 if si > (18 - remainder_giveback) else 0)
                
                net_strokes = s.strokes - extra_strokes
                hole_points = max(0, par + 2 - net_strokes)
                total_stableford += hole_points
                
        players_with_calculations.append({
            "player": p,
            "total_strokes": total_strokes,
            "total_to_par": total_to_par if has_played_any else 0,
            "total_stableford": total_stableford if has_played_any else 0,
            "playing_hcp": playing_hcp,
            "has_played": has_played_any,
            "holes_played": holes_played # Toegevoegd voor de nieuwe sorteersleutel
        })

    # NIEUW: -x["holes_played"] toegevoegd als krachtige secundaire sorteersleutel (tie-breaker)
    if t.format == "stableford":
        players_with_calculations.sort(key=lambda x: (
            x["player"].status != "ACTIVE", 
            -x["total_stableford"] if x["has_played"] else 9999, 
            -x["holes_played"], # Wie het verste is (meeste holes), komt BAVEN aan
            x["total_strokes"]
        ))
    else:
        players_with_calculations.sort(key=lambda x: (
            x["player"].status != "ACTIVE", 
            x["total_to_par"] if x["has_played"] else 9999, 
            -x["holes_played"], # Wie het verste is (meeste holes), komt BOVEN aan
            x["total_strokes"]
        ))

    # Gelijkspel (Tied) Logica
    score_counts = {}
    for item in players_with_calculations:
        p = item["player"]
        if p.status == "ACTIVE" and item["has_played"]:
            score = item["total_stableford"] if t.format == "stableford" else item["total_to_par"]
            score_counts[score] = score_counts.get(score, 0) + 1

    rankings_data = []
    prev_score = None
    displayed_rank = 1

    for idx, item in enumerate(players_with_calculations):
        p = item["player"]
        
        if p.status != "ACTIVE" or not item["has_played"]:
            pos_val = "-"
        else:
            score = item["total_stableford"] if t.format == "stableford" else item["total_to_par"]
            if prev_score is not None and score == prev_score:
                pass 
            else:
                displayed_rank = idx + 1
            
            if score_counts.get(score, 0) > 1:
                pos_val = f"T{displayed_rank}"
            else:
                pos_val = str(displayed_rank)
                
            prev_score = score

        round_scores = {1: {}, 2: {}, 3: {}, 4: {}}
        for s in p.scores:
            if s.strokes > 0:
                round_scores[s.round_number][s.hole_number] = s.strokes

        thru_val = "-"
        for r in [4, 3, 2, 1]:
            if round_scores[r]:
                played_count = len(round_scores[r])
                thru_val = "F" if played_count == 18 else str(played_count)
                break

        rankings_data.append({
            "player_id": p.id,
            "pos": pos_val,
            "name": f"{p.first_name} {p.last_name}",
            "status": p.status,
            "handicap": p.handicap or 0.0,
            "playing_hcp": item["playing_hcp"],
            "thru": thru_val,
            "total_to_par": item["total_to_par"],
            "total_stableford": item["total_stableford"],
            "total_strokes": item["total_strokes"] if item["total_strokes"] > 0 else None,
            "round_scores": round_scores
        })

    return {
        "tournament_name": t.name,
        "format": t.format,
        "num_rounds": t.num_rounds,
        "holes": holes_data,
        "rankings": rankings_data
    }


@router.put("/{tournament_id}/update-cut")
def update_tournament_cut(
    tournament_id: int, body: CutUpdateBody, db: Session = Depends(get_db)
):
    """Update de cut-instellingen van een specifiek toernooi."""
    t = (
        db.query(models.Tournament)
        .filter(models.Tournament.id == tournament_id)
        .first()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")

    t.cut_percentage = body.cut_percentage
    t.has_cut = body.has_cut
    db.commit()
    return {"message": "Cut percentage succesvol bijgewerkt"}


@router.get("/{tournament_id}/cut-preview")
def get_tournament_cut_preview(
    tournament_id: int, db: Session = Depends(get_db)
):
    t = (
        db.query(models.Tournament)
        .filter(models.Tournament.id == tournament_id)
        .first()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")

    players = (
        db.query(models.Player)
        .filter(
            models.Player.tournament_id == tournament_id,
            models.Player.status == "ACTIVE",
        )
        .all()
    )

    players_with_scores = []
    for p in players:
        total_strokes = (
            sum([s.strokes for s in p.scores if s.strokes > 0]) if p.scores else 0
        )
        has_played = any(s.strokes > 0 for s in p.scores)
        score_sort = total_strokes if has_played else 9999
        players_with_scores.append((p, score_sort))

    players_with_scores.sort(key=lambda x: x[1])

    total_count = len(players_with_scores)
    survive_count = math.ceil(total_count * (t.cut_percentage / 100.0))

    safe_players = players_with_scores[:survive_count]
    cut_players = players_with_scores[survive_count:]

    return {
        "will_survive_count": len(safe_players),
        "will_cut_count": len(cut_players),
        "safe_names": [
            f"{p[0].first_name} {p[0].last_name}" for p in safe_players
        ],
        "cut_names": [
            f"{p[0].first_name} {p[0].last_name}" for p in cut_players
        ],
    }


@router.post("/{tournament_id}/apply-cut")
def apply_tournament_cut(tournament_id: int, db: Session = Depends(get_db)):
    preview = get_tournament_cut_preview(tournament_id, db)

    for full_name in preview["cut_names"]:
        first, last = full_name.split(" ", 1)
        player = (
            db.query(models.Player)
            .filter(
                models.Player.tournament_id == tournament_id,
                models.Player.first_name == first,
                models.Player.last_name == last,
            )
            .first()
        )
        if player:
            player.status = "CUT"

    db.commit()
    return {
        "message": "De cut is succesvol en definitief toegepast op de stand!"
    }


@router.delete("/{tournament_id}")
def delete_tournament(
    tournament_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verwijder een toernooi volledig."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Niet geautoriseerd")

    t = (
        db.query(models.Tournament)
        .filter(models.Tournament.id == tournament_id)
        .first()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")

    db.delete(t)
    db.commit()
    return {"message": "Toernooi succesvol gewist"}