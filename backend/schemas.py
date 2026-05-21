from pydantic import BaseModel
from typing import Optional, List

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    token: Optional[str] = None
    class Config:
        from_attributes = True

class ScoreInput(BaseModel):
    hole_number: int
    strokes: int
    round_number: int = 1

class ScoreResponse(BaseModel):
    hole_number: int
    strokes: int
    round_number: int
    class Config:
        from_attributes = True

class HoleBase(BaseModel):
    hole_number: int
    par: int
    stroke_index: int

class HoleCreate(HoleBase):
    pass

class Hole(HoleBase):
    id: int
    course_id: int
    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    name: str
    num_holes: int
    course_rating_men: float
    slope_rating_men: int
    course_rating_women: float
    slope_rating_women: int

class CourseCreate(CourseBase):
    holes: List[HoleCreate]

class Course(CourseBase):
    id: int
    holes: List[Hole] = []
    class Config:
        from_attributes = True

class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    handicap: Optional[float] = None
    status: Optional[str] = "ACTIVE"
    gender: Optional[str] = "M"

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int
    tournament_id: int
    scores: List[ScoreResponse] = []
    class Config:
        from_attributes = True

class TournamentBase(BaseModel):
    name: str
    date: Optional[str] = None
    course_id: Optional[int] = None
    format: str
    has_cut: bool = False
    cut_percentage: Optional[int] = None
    num_rounds: int = 1
    is_public: bool = False # NIEUW

class TournamentCreate(TournamentBase):
    pass

class Tournament(TournamentBase):
    id: int
    course_id: Optional[int] = None
    players: List[Player] = []
    course: Optional[Course] = None
    class Config:
        from_attributes = True