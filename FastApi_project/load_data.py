# load_data.py

from sqlalchemy.orm import Session
from FastApi_project.database import SessionLocal, engine
import models
import schemas
import crud

def load_data():
    db = SessionLocal()
    
    # Добавляем студентов
    students = [
        schemas.StudentCreate(name="John Doe"),
        schemas.StudentCreate(name="Jane Smith"),
        # добавьте больше записей при необходимости
    ]
    created_students = []
    for student in students:
        created_student = crud.create_student(db=db, student=student)
        created_students.append(created_student)
    
    # Добавляем оценки
    scores = [
        schemas.ScoreCreate(value=90, student_id=created_students[0].id),
        schemas.ScoreCreate(value=85, student_id=created_students[1].id),
        # добавьте больше записей при необходимости
    ]
    for score in scores:
        crud.create_score(db=db, score=score)
    
    db.close()

if __name__ == "__main__":
    load_data()
