from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

# creates job_tracker.db and both tables the first time this runs
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# serves static/index.html (the frontend) at /static/index.html
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def root():
    return {"message": "Job Application Tracker API. See /docs or /static/index.html"}


# ---------------------------------------------------------------
# Job postings -- read-only, comes from the seeded Kaggle dataset
# ---------------------------------------------------------------
@app.get("/postings", response_model=List[schemas.JobPostingOut])
def list_postings(
    search: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(models.JobPosting)
    if search:
        query = query.filter(models.JobPosting.title.ilike(f"%{search}%"))
    if location:
        query = query.filter(models.JobPosting.location.ilike(f"%{location}%"))
    return query.limit(limit).all()


@app.get("/postings/{posting_id}", response_model=schemas.JobPostingOut)
def get_posting(posting_id: int, db: Session = Depends(get_db)):
    posting = db.query(models.JobPosting).filter(models.JobPosting.id == posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Posting not found")
    return posting


# ---------------------------------------------------------------
# Applications -- the student's own tracked data, full CRUD
# ---------------------------------------------------------------
@app.get("/applications", response_model=List[schemas.ApplicationOut])
def list_applications(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Application)
    if status:
        query = query.filter(models.Application.status == status)
    return query.order_by(models.Application.date_applied.desc()).all()


@app.post("/applications", response_model=schemas.ApplicationOut, status_code=201)
def create_application(data: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    posting = db.query(models.JobPosting).filter(models.JobPosting.id == data.posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Posting not found")

    application = models.Application(**data.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@app.put("/applications/{application_id}", response_model=schemas.ApplicationOut)
def update_application(
    application_id: int, data: schemas.ApplicationUpdate, db: Session = Depends(get_db)
):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if data.status is not None:
        application.status = data.status
    if data.notes is not None:
        application.notes = data.notes

    db.commit()
    db.refresh(application)
    return application


@app.delete("/applications/{application_id}", status_code=204)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(application)
    db.commit()


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Count of applications per status, e.g. {"Applied": 5, "Interview": 2}"""
    rows = (
        db.query(models.Application.status, func.count(models.Application.id))
        .group_by(models.Application.status)
        .all()
    )
    return {status: count for status, count in rows}
