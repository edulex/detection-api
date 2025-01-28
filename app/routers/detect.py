from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Form
from app.utils.assesment_logic import cumulative_assessment, normalize_score
import os
import tempfile
import pyttsx3
import shutil
from moviepy.video.io.VideoFileClip import VideoFileClip
from app.services.queue_handler import add_task_to_queue
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.models import SessionLocal
from app.db.crud import create_task
import random
import speech_recognition as sr
import eng_to_ipa as ipa

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
    # dump all the request parameters
    print(f"User ID: {user_id}")
    print(f"Video: {video}")
    print(f"Handwriting Image: {handwriting_image}")
    
    
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


@router.post("/")
async def detect(
    user_id: str = Form(...),
    video: UploadFile = File(None),
    handwriting_image: UploadFile = File(None),
    phonetics_text: str = Form(...),  # Accept phonetics text as form data
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """
    Endpoint for detecting dyslexia. Accepts video, handwriting image, and phonetics text.
    """
    if not video:
        raise HTTPException(status_code=400, detail="Video file is required for processing.")

    # Create user directory
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Initialize file paths
    video_path = os.path.join(user_dir, video.filename)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    # Save task in the database
    task = create_task(
        db=db,
        user_id=user_id,
        video_path=video_path,
    )

    # Add background task for processing video and phonetics
    if background_tasks:
        background_tasks.add_task(process_video_and_phonetics, video_path, phonetics_text)

    return {
        "message": "Processing started!",
        "user_id": user_id,
        "video_path": video_path,
        "phonetics_text": phonetics_text,
    }