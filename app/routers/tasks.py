from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.crud import get_all_tasks
from app.db.models import SessionLocal

router = APIRouter(prefix="/tasks", tags=["Task Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_tasks(db: Session = Depends(get_db)):
    tasks = get_all_tasks(db)
    return {"tasks": [task.__dict__ for task in tasks]}
