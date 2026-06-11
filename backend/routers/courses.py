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
    
    db_course = models.Course(
        name=course.name, 
        alias=course.alias,
        num_holes=course.num_holes, 
        course_rating_men=course.course_rating_men, 
        slope_rating_men=course.slope_rating_men,
        course_rating_women=course.course_rating_women,
        slope_rating_women=course.slope_rating_women
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)

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
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Golfbaan niet gevonden")
    
    db_course.name = course_update.name
    db_course.alias = course_update.alias
    db_course.num_holes = course_update.num_holes
    db_course.course_rating_men = course_update.course_rating_men
    db_course.slope_rating_men = course_update.slope_rating_men
    db_course.course_rating_women = course_update.course_rating_women
    db_course.slope_rating_women = course_update.slope_rating_women
    
    db.query(models.Hole).filter(models.Hole.course_id == course_id).delete()
    
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