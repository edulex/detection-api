from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import SessionLocal
from app.db.crud import get_all_tasks, get_queued_tasks, get_task_by_id
import json

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
    
    # Ensure "result" is returned as a JSON object after validation
    formatted_tasks = []
    for task in tasks:
        try:
            result_json = json.loads(task.result) if task.result else None
        except json.JSONDecodeError:
            result_json = {"error": "Invalid JSON format in result"}

        formatted_tasks.append({
            "id": task.id,
            "user_id": task.user_id,
            "video_path": task.video_path,
            "audio_path": task.audio_path,
            "handwriting_image_path": task.handwriting_image_path,
            "status": task.status,
            "result": result_json,
        })

    return {"tasks": formatted_tasks}


@router.get("/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific task by its task_id.
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        result_json = json.loads(task.result) if task.result else None
    except json.JSONDecodeError:
        result_json = {"error": "Invalid JSON format in result"}

    return {
        "id": task.id,
        "user_id": task.user_id,
        "video_path": task.video_path,
        "audio_path": task.audio_path,
        "handwriting_image_path": task.handwriting_image_path,
        "status": task.status,
        "result": task.result,
    }
