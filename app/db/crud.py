from sqlalchemy.orm import Session
from app.db.models import Task

def create_task(db: Session, user_id: str, video_path: str = None, audio_path: str = None, handwriting_image_path: str = None):
    """
    Add a new task to the database.
    """
    task = Task(
        user_id=user_id,
        video_path=video_path,
        audio_path=audio_path,
        handwriting_image_path=handwriting_image_path,
        status="queued"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def update_task_status(db: Session, task_id: int, status: str, result: str = None):
    """
    Update the status and result of a task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        task.result = result
        db.commit()
        db.refresh(task)
    return task

def get_all_tasks(db: Session):
    """
    Retrieve all tasks.
    """
    return db.query(Task).all()

def get_queued_tasks(db: Session):
    """
    Retrieve tasks in the 'queued' state.
    """
    return db.query(Task).filter(Task.status == "queued").all()

def get_task_by_id(db: Session, task_id: int):
    """
    Retrieve a specific task by its ID.
    """
    return db.query(Task).filter(Task.id == task_id).first()
