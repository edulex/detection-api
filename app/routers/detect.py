from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Form
import os
import shutil
from moviepy.video.io.VideoFileClip import VideoFileClip
from app.services.queue_handler import add_task_to_queue
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.models import SessionLocal
from app.db.crud import create_task

router = APIRouter(prefix="/detect", tags=["Detection"])

BASE_DIR = "app/data/uploads"
os.makedirs(BASE_DIR, exist_ok=True)  # Ensure the base directory exists


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
async def detect(
    user_id: str = Form(...),
    video: UploadFile = File(None),
    handwriting_image: UploadFile = File(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """
    Endpoint for detecting dyslexia. Accepts video and an optional handwriting image.
    """
    if not video and not handwriting_image:
        raise HTTPException(status_code=400, detail="Either a video or handwriting image must be provided.")

    # Create user directory
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Initialize file paths
    video_path = None
    audio_path = None
    handwriting_image_path = None

    # Process video
    if video:
        if not video.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video file.")
        
        video_path = os.path.join(user_dir, video.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        # Extract audio and store it
        audio_path = os.path.splitext(video_path)[0] + ".wav"
        extract_audio(video_path, audio_path)

    # Process handwriting image
    if handwriting_image:
        if not handwriting_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file.")
        
        handwriting_image_path = os.path.join(user_dir, handwriting_image.filename)
        with open(handwriting_image_path, "wb") as buffer:
            shutil.copyfileobj(handwriting_image.file, buffer)

    # Save the task to the database
    task = create_task(
        db=db,
        user_id=user_id,
        video_path=video_path,
        audio_path=audio_path,
    )

    # Add background task for video processing if video is provided
    if video and background_tasks:
        background_tasks.add_task(process_video, user_id, video_path, audio_path)

    return {
        "message": "Processing started!" if video or handwriting_image else "No processing task was initiated.",
        "user_id": user_id,
        "video_path": video_path,
        "audio_path": audio_path,
        "handwriting_image_path": handwriting_image_path,
    }

def extract_audio(video_path: str, audio_path: str):
    """
    Extracts audio from the provided video file and saves it as a .wav file.
    """
    try:
        video = VideoFileClip(video_path)

        # Check if the video contains an audio track
        if video.audio is None:
            raise ValueError("The uploaded video does not contain an audio track.")

        # Extract and save the audio
        video.audio.write_audiofile(audio_path)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting audio: {str(e)}")

def process_video(user_id: str, video_path: str, audio_path: str):
    """
    Placeholder function for processing the video and audio for dyslexia detection.
    """
    print(f"Processing video for user {user_id}: {video_path}")
    print(f"Processing audio for user {user_id}: {audio_path}")
