from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])

def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Alleen admins mogen deze actie uitvoeren")
    return current_user

@router.get("/", response_model=List[schemas.Course])
def get_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@router.post("/", response_model=schemas.Course)
def create_course(
    course: schemas.CourseCreate, 
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(require_admin)):
    db_course = models.Course(name=course.name, num_holes=course.num_holes, course_rating=course.course_rating, slope_rating=course.slope_rating)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    # Voeg alle 9 of 18 holes toe
    for h in course.holes:
        db_hole = models.Hole(
            course_id=db_course.id,
            hole_number=h.hole_number,
            par=h.par,
            stroke_index=h.stroke_index
        )
        db.add(db_hole)
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/{course_id}")
def delete_course(
    course_id: int, 
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(require_admin)
    ):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Baan niet gevonden")
    db.delete(db_course)
    db.commit()
    return {"message": "Golfbaan succesvol verwijderd"}

@router.put("/{course_id}", response_model=schemas.Course)
def update_course(course_id: int, course_update: schemas.CourseCreate, db: Session = Depends(get_db),current_admin: models.User = Depends(require_admin)):
    # 1. Zoek de bestaande baan
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Golfbaan niet gevonden")
    
    # 2. Update de hoofdgegevens
    db_course.name = course_update.name
    db_course.num_holes = course_update.num_holes
    db_course.course_rating = course_update.course_rating
    db_course.slope_rating = course_update.slope_rating
    
    # 3. Verwijder de oude hole-specificaties van deze baan
    db.query(models.Hole).filter(models.Hole.course_id == course_id).delete()
    
    # 4. Voeg de vernieuwde holes toe
    for h in course_update.holes:
        db_hole = models.Hole(
            course_id=course_id,
            hole_number=h.hole_number,
            par=h.par,
            stroke_index=h.stroke_index
        )
        db.add(db_hole)
        
    db.commit()
    db.refresh(db_course)
    return db_course