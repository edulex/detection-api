from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Form
from app.utils.assesment_logic import cumulative_assessment, normalize_score
import os
import shutil
from moviepy import VideoFileClip
from app.services.queue_handler import add_task_to_queue
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.models import SessionLocal
from app.db.crud import create_task
import random

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
    Endpoint for detecting dyslexia. Accepts video and/or handwriting image.
    If no files are provided, uses random scores for testing purposes.
    """
    # Check if neither video nor handwriting image is provided
    if not video and not handwriting_image:
        # Generate random scores and directly return the assessment
        print(f"Simulating results for user {user_id}")
        detection_results = {
            "eye_tracking": normalize_score(random.uniform(0.5, 1.0), 0, 1),
            "handwriting": normalize_score(random.uniform(5, 10), 0, 10),
            "phonetics": normalize_score(random.uniform(0, 10), 0, 10),
            "questionnaire": normalize_score(random.uniform(0, 6), 0, 6),
            "dictation": normalize_score(random.uniform(0, 10), 0, 10),
        }
        assessment_result = cumulative_assessment(detection_results)
        return {
            "message": "Simulated processing started!",
            "user_id": user_id,
            "assessment": assessment_result,
        }

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
        handwriting_image_path=handwriting_image_path,
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


# def process_video(user_id: str, video_path: str, audio_path: str):
#     """
#     Process the video and audio to compute results and perform cumulative assessment.
#     """
#     print(f"Processing video for user {user_id}: {video_path}")
#     print(f"Processing audio for user {user_id}: {audio_path}")

#     # Example detection results (replace with actual model results)
#     detection_results = {
#         "eye_tracking": normalize_score(0.8, 0, 1),  # Replace with actual normalized result
#         "handwriting": normalize_score(9, 0, 10),  # Replace with actual normalized result
#         "phonetics": normalize_score(4, 0, 10),  # Replace with actual normalized result
#         "questionnaire": normalize_score(4, 0, 6),  # Replace with actual normalized result
#         "dictation": normalize_score(3, 0, 10),  # Replace with actual normalized result
#     }

#     # Perform cumulative assessment
#     assessment_result = cumulative_assessment(detection_results)
#     print(f"Assessment Result: {assessment_result}")

#     # Return or save the assessment result as needed
#     return assessment_result

import random

def process_video(user_id: str, video_path: str = None, audio_path: str = None):
    """
    Simulate the processing of video and handwriting image with random scores.
    """
    print(f"Simulating processing for user {user_id}")

    # Simulate random detection results for testing purposes
    detection_results = {
        "eye_tracking": normalize_score(random.uniform(0.5, 1.0), 0, 1),  # Random normalized value for eye tracking
        "handwriting": normalize_score(random.randint(5, 10), 0, 10),  # Random normalized value for handwriting
        "phonetics": normalize_score(random.randint(0, 10), 0, 10),  # Random normalized value for phonetics
        "questionnaire": normalize_score(random.randint(0, 6), 0, 6),  # Random normalized value for questionnaire
        "dictation": normalize_score(random.randint(0, 10), 0, 10),  # Random normalized value for dictation
    }

    # Perform cumulative assessment
    assessment_result = cumulative_assessment(detection_results)
    print(f"Assessment Result: {assessment_result}")

    # Return the assessment result
    return assessment_result


