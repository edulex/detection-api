from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models import SessionLocal
from app.db.crud import get_queued_tasks, update_task_status
from app.services.video_processing import process_video_for_dyslexia
from app.services.handwriting_processing import process_handwriting_for_dyslexia
from app.utils.phonetics_analysis import analyze_phonetics  # Assuming phonetics logic is here
import os

router = APIRouter(prefix="/process", tags=["Task Processing"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
async def process_tasks(db: Session = Depends(get_db)):
    """
    Process all tasks in the 'queued' state.
    """
    tasks = get_queued_tasks(db)  # Fetch only queued tasks
    results = {}

    for task in tasks:
        try:
            # Mark task as processing
            update_task_status(db, task.id, "processing")

            # Initialize result
            result = {}

            # Process the video if the path exists
            if task.video_path:
                # Process video for dyslexia (e.g., eye-tracking analysis)
                video_result = process_video_for_dyslexia(task.video_path)
                result['video_analysis'] = video_result

                # Perform phonetics analysis on the extracted audio
                if task.audio_path and os.path.exists(task.audio_path):
                    phonetics_result = analyze_phonetics(
                        user_id=task.user_id,
                        recorded_audio_path=task.audio_path,
                        level=1  # Example difficulty level, can be parameterized
                    )
                    result['phonetics_analysis'] = phonetics_result

            # Process handwriting if the path exists
            if task.handwriting_image_path:
                handwriting_result = process_handwriting_for_dyslexia(task.handwriting_image_path)
                result['handwriting_analysis'] = handwriting_result

            # Mark task as completed with results
            update_task_status(db, task.id, "completed", result=str(result))
            results[task.id] = "completed"
        except Exception as e:
            # Mark task as failed with error details
            update_task_status(db, task.id, "failed", result=str(e))
            results[task.id] = f"failed: {str(e)}"

    return {"message": "Processing completed.", "results": results}
