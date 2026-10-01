from datetime import date
from typing import Optional

from pydantic import BaseModel


class JobPostingOut(BaseModel):
    id: int
    title: str
    location: Optional[str] = None
    department: Optional[str] = None
    industry: Optional[str] = None
    employment_type: Optional[str] = None
    required_experience: Optional[str] = None
    required_education: Optional[str] = None
    salary_range: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True  # lets Pydantic read straight from the ORM object


class ApplicationCreate(BaseModel):
    posting_id: int
    company_name: str
    status: str = "Applied"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    posting_id: int
    company_name: str
    status: str
    date_applied: date
    notes: Optional[str] = None
    posting: Optional[JobPostingOut] = None

    class Config:
        from_attributes = True
