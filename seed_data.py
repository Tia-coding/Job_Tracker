"""
Loads real job postings from a Kaggle CSV into the job_postings table,
instead of hand-typing fake data.

Dataset used by default: "Real / Fake Job Posting Prediction" by shivamb
https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction
(free Kaggle account needed to download)

Steps:
1. Open the link above, click Download, unzip it.
2. Copy fake_job_postings.csv into this project folder (same folder as main.py).
3. Run:  python seed_data.py

Using a different Kaggle jobs dataset instead? Just edit CSV_FILE and
COLUMN_MAP below to match its filename and column names.
"""

import pandas as pd

from database import SessionLocal, engine, Base
from models import JobPosting

Base.metadata.create_all(bind=engine)

CSV_FILE = "fake_job_postings.csv"

# our_column -> column name as it appears in the CSV
COLUMN_MAP = {
    "title": "title",
    "location": "location",
    "department": "department",
    "industry": "industry",
    "employment_type": "employment_type",
    "required_experience": "required_experience",
    "required_education": "required_education",
    "salary_range": "salary_range",
    "description": "description",
}

MAX_ROWS_TO_SEED = 300  # the full dataset has ~18,000 rows -- keep a manageable slice


def safe_str(value):
    """Handles NaN cells so we don't store the literal string 'nan'."""
    if pd.isna(value):
        return None
    return str(value)


def seed():
    df = pd.read_csv(CSV_FILE)
    df = df.head(MAX_ROWS_TO_SEED)

    db = SessionLocal()
    already_there = db.query(JobPosting).count()
    if already_there > 0:
        print(f"job_postings already has {already_there} rows -- skipping seed "
              f"(delete job_tracker.db if you want to reseed from scratch).")
        db.close()
        return

    inserted = 0
    for _, row in df.iterrows():
        posting = JobPosting(
            title=safe_str(row.get(COLUMN_MAP["title"])) or "Untitled position",
            location=safe_str(row.get(COLUMN_MAP["location"])),
            department=safe_str(row.get(COLUMN_MAP["department"])),
            industry=safe_str(row.get(COLUMN_MAP["industry"])),
            employment_type=safe_str(row.get(COLUMN_MAP["employment_type"])),
            required_experience=safe_str(row.get(COLUMN_MAP["required_experience"])),
            required_education=safe_str(row.get(COLUMN_MAP["required_education"])),
            salary_range=safe_str(row.get(COLUMN_MAP["salary_range"])),
            description=(safe_str(row.get(COLUMN_MAP["description"])) or "")[:600],
            source="Kaggle: real-or-fake-fake-jobposting-prediction",
        )
        db.add(posting)
        inserted += 1

    db.commit()
    db.close()
    print(f"Seeded {inserted} job postings into job_tracker.db")


if __name__ == "__main__":
    seed()
