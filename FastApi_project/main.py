# main.py
from fastapi import FastAPI, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from database import SessionLocal, engine
from api import router as api_router  # Import the API router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount the API router
app.include_router(api_router, prefix="/api", tags=["api"])

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/students/search/", response_class=HTMLResponse, include_in_schema=False)
async def search_students_by_name(request: Request, name: str = Query(..., alias="name"), db: Session = Depends(get_db)):
    students = crud.search_students_by_name(db, name)
    return templates.TemplateResponse("students/students_search.html", {"request": request, "students": students})

@app.get("/students/", response_class=HTMLResponse, include_in_schema=False)
async def get_students(request: Request, db: Session = Depends(get_db)):
    students = crud.get_students(db)
    return templates.TemplateResponse("students.html", {"request": request, "students": students})

@app.get("/students/{student_id}", response_class=HTMLResponse, include_in_schema=False)
async def get_student_details(request: Request, student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    scores = crud.get_scores_by_student(db, student_id)
    return templates.TemplateResponse("students/student_detail.html", {"request": request, "student": student, "scores": scores})

@app.post("/students/", response_class=HTMLResponse, include_in_schema=False)
async def create_student(name: str = Form(...), db: Session = Depends(get_db)):
    student_create = schemas.StudentCreate(name=name)
    crud.create_student(db, student_create)
    return RedirectResponse(url="/students/", status_code=303)

@app.get("/students/{student_id}/edit", response_class=HTMLResponse, include_in_schema=False)
async def edit_student_form(request: Request, student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse("students/edit_student.html", {"request": request, "student": student})

@app.post("/students/{student_id}/edit", response_class=HTMLResponse, include_in_schema=False)
async def edit_student(student_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    student_update = schemas.StudentCreate(name=name)
    crud.update_student(db, student_id, student_update)
    return RedirectResponse(url=f"/students/{student_id}", status_code=303)

@app.post("/students/{student_id}/delete", response_class=HTMLResponse, include_in_schema=False)
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    crud.delete_student(db, student_id)
    return RedirectResponse(url="/students/", status_code=303)

@app.post("/students/{student_id}/scores/", response_class=HTMLResponse, include_in_schema=False)
async def create_score(student_id: int, value: int = Form(...), db: Session = Depends(get_db)):
    score_create = schemas.ScoreCreate(value=value, student_id=student_id)
    crud.create_score(db, score_create)
    return RedirectResponse(url=f"/students/{student_id}", status_code=303)

@app.post("/scores/{score_id}/edit", response_class=HTMLResponse, include_in_schema=False)
async def edit_score(score_id: int, value: int = Form(...), db: Session = Depends(get_db)):
    score = crud.get_score(db, score_id)
    if score:
        score_update = schemas.ScoreCreate(value=value, student_id=score.student_id)
        crud.update_score(db, score_id, score_update)
        return RedirectResponse(url=f"/students/{score.student_id}", status_code=303)
    raise HTTPException(status_code=404, detail="Score not found")

@app.post("/scores/{score_id}/delete", response_class=HTMLResponse, include_in_schema=False)
async def delete_score(score_id: int, db: Session = Depends(get_db)):
    score = crud.get_score(db, score_id)
    if score:
        student_id = score.student_id
        crud.delete_score(db, score_id)
        return RedirectResponse(url=f"/students/{student_id}", status_code=303)
    raise HTTPException(status_code=404, detail="Score not found")

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

