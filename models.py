import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import relationship

from database import Base


class JobPosting(Base):
    """A job listing. This table is filled once from a real Kaggle
    dataset (see seed_data.py) -- it is NOT something the student
    creates by hand."""
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    location = Column(String)
    department = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    employment_type = Column(String, nullable=True)
    required_experience = Column(String, nullable=True)
    required_education = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String, default="Kaggle dataset")

    applications = relationship("Application", back_populates="posting")


class Application(Base):
    """One application the student personally tracks: which posting
    they applied to, what company, and what stage it's at."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    posting_id = Column(Integer, ForeignKey("job_postings.id"))
    company_name = Column(String)  # dataset has no company names, so this is typed in by the user
    status = Column(String, default="Applied")  # Applied / Interview / Offer / Rejected / Withdrawn
    date_applied = Column(Date, default=datetime.date.today)
    notes = Column(Text, nullable=True)

    posting = relationship("JobPosting", back_populates="applications")
