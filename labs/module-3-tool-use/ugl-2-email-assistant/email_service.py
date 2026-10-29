"""Simulated email backend for the M3 email-assistant lab.

A small FastAPI app backed by an in-memory SQLite database, exercised
through Starlette's TestClient (no real socket/server process needed).
utils.py and email_tools.py both talk to `client` defined here.
"""

from datetime import datetime, timedelta, date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = "sqlite:///:memory:"
# StaticPool keeps a single shared connection alive so every session sees
# the same in-memory database (plain sqlite3 :memory: is per-connection).
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class EmailModel(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


class EmailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: str
    recipient: str
    subject: str
    body: str
    timestamp: datetime
    read: bool


class SendEmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str
    sender: str = "you@email.com"


app = FastAPI(title="Simulated Email Service")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SEED_EMAILS = [
    dict(
        sender="eric@work.com",
        recipient="you@email.com",
        subject="Happy Hour",
        body="We're planning drinks this Friday!",
        read=False,
        timestamp=datetime.utcnow() - timedelta(days=2),
    ),
    dict(
        sender="boss@email.com",
        recipient="you@email.com",
        subject="Quarterly Report Due",
        body="Please send over the quarterly report by end of week.",
        read=False,
        timestamp=datetime.utcnow() - timedelta(days=1),
    ),
    dict(
        sender="alice@work.com",
        recipient="you@email.com",
        subject="Project Update",
        body="Here's the latest update on the project timeline.",
        read=True,
        timestamp=datetime.utcnow() - timedelta(hours=5),
    ),
    dict(
        sender="you@email.com",
        recipient="dave@work.com",
        subject="Lunch tomorrow?",
        body="Are you free for lunch tomorrow at noon?",
        read=True,
        timestamp=datetime.utcnow() - timedelta(hours=1),
    ),
]


def _seed(db):
    db.query(EmailModel).delete()
    for e in SEED_EMAILS:
        db.add(EmailModel(**e))
    db.commit()


with SessionLocal() as _db:
    _seed(_db)


@app.post("/send", response_model=EmailOut)
def send_email_endpoint(req: SendEmailRequest, db=Depends(get_db)):
    email = EmailModel(
        sender=req.sender,
        recipient=req.recipient,
        subject=req.subject,
        body=req.body,
        timestamp=datetime.utcnow(),
        read=False,
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


@app.get("/emails/unread", response_model=list[EmailOut])
def list_unread(db=Depends(get_db)):
    return (
        db.query(EmailModel)
        .filter(EmailModel.read.is_(False))
        .order_by(EmailModel.timestamp.desc())
        .all()
    )


@app.get("/emails/search", response_model=list[EmailOut])
def search_emails(q: str, db=Depends(get_db)):
    like = f"%{q.lower()}%"
    return (
        db.query(EmailModel)
        .filter(
            (EmailModel.subject.ilike(like))
            | (EmailModel.body.ilike(like))
            | (EmailModel.sender.ilike(like))
        )
        .order_by(EmailModel.timestamp.desc())
        .all()
    )


@app.get("/emails/filter", response_model=list[EmailOut])
def filter_emails(
    recipient: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db=Depends(get_db),
):
    query = db.query(EmailModel)
    if recipient:
        query = query.filter(EmailModel.recipient == recipient)
    if date_from:
        query = query.filter(EmailModel.timestamp >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(EmailModel.timestamp <= datetime.combine(date_to, datetime.max.time()))
    return query.order_by(EmailModel.timestamp.desc()).all()


@app.get("/emails/{email_id}", response_model=EmailOut)
def get_email(email_id: int, db=Depends(get_db)):
    email = db.query(EmailModel).filter(EmailModel.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@app.get("/emails", response_model=list[EmailOut])
def list_all(db=Depends(get_db)):
    return db.query(EmailModel).order_by(EmailModel.timestamp.desc()).all()


@app.patch("/emails/{email_id}/read", response_model=EmailOut)
def mark_read(email_id: int, db=Depends(get_db)):
    email = db.query(EmailModel).filter(EmailModel.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.read = True
    db.commit()
    db.refresh(email)
    return email


@app.patch("/emails/{email_id}/unread", response_model=EmailOut)
def mark_unread(email_id: int, db=Depends(get_db)):
    email = db.query(EmailModel).filter(EmailModel.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.read = False
    db.commit()
    db.refresh(email)
    return email


@app.delete("/emails/{email_id}")
def delete_email(email_id: int, db=Depends(get_db)):
    email = db.query(EmailModel).filter(EmailModel.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    db.delete(email)
    db.commit()
    return {"deleted": True, "id": email_id}


@app.get("/reset_database")
def reset_database_endpoint(db=Depends(get_db)):
    _seed(db)
    return {"status": "reset", "count": len(SEED_EMAILS)}


client = TestClient(app)
