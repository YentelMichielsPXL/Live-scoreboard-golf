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

class StatusUpdateBody(BaseModel):
    status: str

class CutUpdateBody(BaseModel):
    cut_percentage: int
    has_cut: bool

class VisibilityUpdateBody(BaseModel):
    is_public: bool

class TournamentCreateBody(BaseModel):
    name: str
    date: str
    course_id: int
    format: str
    has_cut: bool
    cut_percentage: int
    num_rounds: int
    is_public: bool = False # NIEUW

def golf_round(value: float) -> int:
    if value >= 0:
        return int(value + 0.5)
    else:
        return int(value - 0.5)

@router.get("/")
def get_tournaments(db: Session = Depends(get_db)):
    tournaments = db.query(models.Tournament).order_by(models.Tournament.id.desc()).all()
    results = []
    
    for t in tournaments:
        players = db.query(models.Player).filter(models.Player.tournament_id == t.id).all()
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
            "is_public": getattr(t, 'is_public', False), # NIEUW
            "course": {"name": t.course.name} if hasattr(t, "course") and t.course else None,
            "players": [p.id for p in players]
        })
    return results

@router.get("/active/metadata")
def get_active_tournament_metadata(db: Session = Depends(get_db)):
    t = db.query(models.Tournament).order_by(models.Tournament.id.desc()).first()
    if not t:
        raise HTTPException(status_code=404, detail="Er zijn nog geen toernooien aangemaakt")
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
    t = db.query(models.Tournament).order_by(models.Tournament.id.desc()).first()
    if not t:
        raise HTTPException(status_code=404, detail="Geen actief toernooi gevonden")
    return get_tournament_leaderboard(t.id, db)

@router.post("/")
def create_tournament(
    body: TournamentCreateBody,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen toernooien aanmaken")
    try:
        parsed_date = datetime.strptime(body.date, "%Y-%m-%d").date()
    except Exception:
        parsed_date = body.date

    new_tournament = models.Tournament(
        name=body.name, date=parsed_date, course_id=body.course_id,
        format=body.format, has_cut=body.has_cut, cut_percentage=body.cut_percentage,
        num_rounds=body.num_rounds, is_public=body.is_public # NIEUW
    )
    db.add(new_tournament)
    db.commit()
    db.refresh(new_tournament)
    return {"message": "Toernooi succesvol aangemaakt", "id": new_tournament.id}

@router.put("/players/{player_id}/status")
def change_player_status(
    player_id: int, body: StatusUpdateBody,
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen spelersstatussen wijzigen")
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Speler niet gevonden")
    player.status = body.status
    db.commit()
    return {"message": f"Status succesvol gewijzigd naar {body.status}"}

@router.get("/{tournament_id}/players")
def get_tournament_players(tournament_id: int, db: Session = Depends(get_db)):
    players = db.query(models.Player).filter(models.Player.tournament_id == tournament_id).all()
    return [
        {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "handicap": p.handicap,
            "status": p.status,
            "gender": p.gender,
            "scores": [{"round_number": s.round_number, "hole_number": s.hole_number, "strokes": s.strokes} for s in p.scores],
        }
        for p in players
    ]

@router.get("/{tournament_id}/leaderboard")
def get_tournament_leaderboard(tournament_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")

    holes_data = []
    if hasattr(t, "course") and t.course and hasattr(t.course, "holes"):
        for h in sorted(t.course.holes, key=lambda x: x.hole_number):
            holes_data.append({"hole_number": h.hole_number, "par": h.par, "stroke_index": h.stroke_index})
    elif hasattr(t, "course_id") and t.course_id:
        try:
            holes = db.query(models.Hole).filter(models.Hole.course_id == t.course_id).order_by(models.Hole.hole_number).all()
            for h in holes:
                holes_data.append({"hole_number": h.hole_number, "par": h.par, "stroke_index": h.stroke_index})
        except Exception:
            pass

    if not holes_data:
        holes_data = [{"hole_number": i, "par": 4, "stroke_index": i} for i in range(1, 19)]

    total_par = sum([h["par"] for h in holes_data])

    players = db.query(models.Player).filter(models.Player.tournament_id == tournament_id).all()

    current_tournament_round = 1
    for p in players:
        for s in p.scores:
            if s.strokes > 0 and s.round_number > current_tournament_round:
                current_tournament_round = s.round_number

    tournament_active = True
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
            tournament_active = False

    players_with_calculations = []
    for p in players:
        total_strokes = sum([s.strokes for s in p.scores if s.strokes > 0])
        exact_hcp = p.handicap if p.handicap is not None else 0.0
        
        course_slope = 113
        course_cr = total_par
        if t.course:
            if p.gender == 'F':
                course_slope = getattr(t.course, "slope_rating_women", 113)
                course_cr = getattr(t.course, "course_rating_women", total_par)
            else:
                course_slope = getattr(t.course, "slope_rating_men", 113)
                course_cr = getattr(t.course, "course_rating_men", total_par)
        
        raw_playing_hcp = exact_hcp * (course_slope / 113.0) + (course_cr - total_par)
        playing_hcp = golf_round(raw_playing_hcp)
        
        total_to_par = 0
        total_stableford = 0
        has_played_any = False
        holes_played = 0
        
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
            "holes_played": holes_played
        })

    men_calc = [p for p in players_with_calculations if p["player"].gender == "M"]
    women_calc = [p for p in players_with_calculations if p["player"].gender == "F"]

    projected_cut_men = None
    projected_cut_women = None

    if t.has_cut and t.cut_percentage:
        def get_projected_cut(group_calc):
            active_players = [p for p in group_calc if p["player"].status == "ACTIVE"]
            if not active_players:
                return None
            if not all(p["holes_played"] >= 9 for p in active_players):
                return None

            if t.format == "stableford":
                sorted_players = sorted(active_players, key=lambda x: -x["total_stableford"])
            else:
                sorted_players = sorted(active_players, key=lambda x: x["total_to_par"])

            survive_count = math.ceil(len(sorted_players) * (t.cut_percentage / 100.0))
            if survive_count > 0 and survive_count <= len(sorted_players):
                cut_player = sorted_players[survive_count - 1]
                return cut_player["total_stableford"] if t.format == "stableford" else cut_player["total_to_par"]
            return None

        projected_cut_men = get_projected_cut(men_calc)
        projected_cut_women = get_projected_cut(women_calc)

    def rank_group(calc_list):
        if t.format == "stableford":
            calc_list.sort(key=lambda x: (
                x["player"].status != "ACTIVE", 
                -x["total_stableford"] if x["has_played"] else 9999, 
                x["player"].handicap if not x["has_played"] else 0,
                -x["holes_played"], 
                x["total_strokes"]
            ))
        else:
            calc_list.sort(key=lambda x: (
                x["player"].status != "ACTIVE", 
                x["total_to_par"] if x["has_played"] else 9999, 
                x["player"].handicap if not x["has_played"] else 0,
                -x["holes_played"], 
                x["total_strokes"]
            ))

        score_counts = {}
        for item in calc_list:
            p = item["player"]
            if p.status == "ACTIVE" and item["has_played"]:
                score = item["total_stableford"] if t.format == "stableford" else item["total_to_par"]
                score_counts[score] = score_counts.get(score, 0) + 1

        rankings = []
        prev_score = None
        displayed_rank = 1

        for idx, item in enumerate(calc_list):
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

            highest_played_round = 1
            for r in [4, 3, 2, 1]:
                if round_scores[r]:
                    highest_played_round = r
                    break
            
            played_count = len(round_scores[highest_played_round])
            
            if p.status != "ACTIVE":
                thru_val = "-"
            elif played_count == 18 and highest_played_round < current_tournament_round:
                thru_val = "-"
            elif played_count == 18:
                thru_val = "F"
            elif played_count == 0:
                thru_val = "-"
            else:
                thru_val = str(played_count)

            rankings.append({
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
                "round_scores": round_scores,
                "gender": p.gender
            })
        return rankings

    return {
        "tournament_name": t.name,
        "format": t.format,
        "num_rounds": t.num_rounds,
        "holes": holes_data,
        "rankings_men": rank_group(men_calc),
        "rankings_women": rank_group(women_calc),
        "projected_cut_men": projected_cut_men,
        "projected_cut_women": projected_cut_women,
        "is_active": tournament_active
    }

@router.put("/{tournament_id}/visibility")
def update_tournament_visibility(tournament_id: int, body: VisibilityUpdateBody, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen dit aanpassen")
    t = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")
    t.is_public = body.is_public
    db.commit()
    return {"message": "Zichtbaarheid geüpdatet", "is_public": t.is_public}

@router.put("/{tournament_id}/update-cut")
def update_tournament_cut(tournament_id: int, body: CutUpdateBody, db: Session = Depends(get_db)):
    t = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")
    t.cut_percentage = body.cut_percentage
    t.has_cut = body.has_cut
    db.commit()
    return {"message": "Cut percentage succesvol bijgewerkt"}

@router.get("/{tournament_id}/cut-preview")
def get_tournament_cut_preview(tournament_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")

    players = db.query(models.Player).filter(
        models.Player.tournament_id == tournament_id, models.Player.status == "ACTIVE",
    ).all()

    men_scores = []
    women_scores = []

    for p in players:
        total_strokes = sum([s.strokes for s in p.scores if s.strokes > 0]) if p.scores else 0
        has_played = any(s.strokes > 0 for s in p.scores)
        score_sort = total_strokes if has_played else 9999
        
        if p.gender == 'F':
            women_scores.append((p, score_sort))
        else:
            men_scores.append((p, score_sort))

    men_scores.sort(key=lambda x: x[1])
    women_scores.sort(key=lambda x: x[1])

    men_survive = math.ceil(len(men_scores) * (t.cut_percentage / 100.0))
    women_survive = math.ceil(len(women_scores) * (t.cut_percentage / 100.0))

    safe_players = []
    cut_players = []

    men_cut_score = men_scores[men_survive - 1][1] if men_survive > 0 and len(men_scores) > 0 else None
    for i, p_tuple in enumerate(men_scores):
        if i < men_survive or p_tuple[1] == men_cut_score:
            safe_players.append(p_tuple)
        else:
            cut_players.append(p_tuple)

    women_cut_score = women_scores[women_survive - 1][1] if women_survive > 0 and len(women_scores) > 0 else None
    for i, p_tuple in enumerate(women_scores):
        if i < women_survive or p_tuple[1] == women_cut_score:
            safe_players.append(p_tuple)
        else:
            cut_players.append(p_tuple)

    return {
        "will_survive_count": len(safe_players),
        "will_cut_count": len(cut_players),
        "safe_names": [f"{p[0].first_name} {p[0].last_name} ({p[0].gender})" for p in safe_players],
        "cut_names": [f"{p[0].first_name} {p[0].last_name} ({p[0].gender})" for p in cut_players],
        "cut_ids": [p[0].id for p in cut_players]
    }

@router.post("/{tournament_id}/apply-cut")
def apply_tournament_cut(tournament_id: int, db: Session = Depends(get_db)):
    preview = get_tournament_cut_preview(tournament_id, db)
    
    for pid in preview.get("cut_ids", []):
        player = db.query(models.Player).filter(
            models.Player.id == pid,
            models.Player.tournament_id == tournament_id
        ).first()
        if player:
            player.status = "CUT"
            
    db.commit()
    return {"message": "De cut is succesvol en definitief toegepast op de stand!"}

@router.post("/{tournament_id}/remove-cut")
def remove_tournament_cut(tournament_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Niet geautoriseerd om de cut ongedaan te maken")
        
    t = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")

    cut_players = db.query(models.Player).filter(
        models.Player.tournament_id == tournament_id,
        models.Player.status == "CUT"
    ).all()

    for player in cut_players:
        player.status = "ACTIVE"
        
    db.commit()
    return {"message": f"Cut succesvol ongedaan gemaakt. {len(cut_players)} spelers zijn weer actief!"}

@router.delete("/{tournament_id}")
def delete_tournament(
    tournament_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Niet geautoriseerd")
    t = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Toernooi niet gevonden")
    db.delete(t)
    db.commit()
    return {"message": "Toernooi succesvol gewist"}