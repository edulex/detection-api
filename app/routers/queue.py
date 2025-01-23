from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models import SessionLocal
from app.db.crud import get_all_tasks, get_queued_tasks

router = APIRouter(prefix="/queue", tags=["Queue Management"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_tasks(db: Session = Depends(get_db)):
    """
    List all tasks in the database along with their statuses.
    """
    tasks = get_all_tasks(db)
    return {
        "tasks": [
            {
                "id": task.id,
                "user_id": task.user_id,
                "video_path": task.video_path,
                "audio_path": task.audio_path,
                "handwriting_image_path": task.handwriting_image_path,
                "status": task.status,
                "result": task.result,
            }
            for task in tasks
        ]
    }
