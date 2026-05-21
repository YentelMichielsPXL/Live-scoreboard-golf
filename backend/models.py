from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="scorer")
    token = Column(String, nullable=True)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    num_holes = Column(Integer, default=18)
    
    course_rating_men = Column(Float, nullable=False, default=72.0)
    slope_rating_men = Column(Integer, nullable=False, default=113)
    course_rating_women = Column(Float, nullable=False, default=72.0)
    slope_rating_women = Column(Integer, nullable=False, default=113)

    holes = relationship("Hole", back_populates="course", cascade="all, delete-orphan")
    tournaments = relationship("Tournament", back_populates="course")

class Hole(Base):
    __tablename__ = "holes"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    hole_number = Column(Integer, nullable=False)
    par = Column(Integer, nullable=False, default=4)
    stroke_index = Column(Integer, nullable=False)

    course = relationship("Course", back_populates="holes")

class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    date = Column(String, nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    format = Column(String, nullable=False, default="stableford")
    has_cut = Column(Boolean, default=False)
    cut_percentage = Column(Integer, nullable=True)
    num_rounds = Column(Integer, default=1, nullable=False)
    is_public = Column(Boolean, default=False) # NIEUW: Standaard verborgen

    course = relationship("Course", back_populates="tournaments")
    players = relationship("Player", back_populates="tournament", cascade="all, delete-orphan")

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    handicap = Column(Float, nullable=True)
    gender = Column(String, nullable=False, default="M")
    tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    
    tournament = relationship("Tournament", back_populates="players")
    scores = relationship("Score", back_populates="player", cascade="all, delete-orphan")

class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    hole_number = Column(Integer, nullable=False)
    strokes = Column(Integer, nullable=False)
    round_number = Column(Integer, default=1, nullable=False)

    player = relationship("Player", back_populates="scores")
    
    __table_args__ = (UniqueConstraint('player_id', 'round_number', 'hole_number', name='_player_round_hole_uc'),)