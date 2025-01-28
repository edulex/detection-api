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


#-----------------------------------------------------------------
# PHONETICS ENDPOINT
#-----------------------------------------------------------------
@router.post("/phonetics/")
async def analyze_phonetics(
    user_id: str = Form(...),
    recorded_audio: UploadFile = File(...),
    level: int = Form(1)
):
    """
    Analyze the user's pronunciation by comparing it to a predefined set of words.
    Returns a phonetics inaccuracy score (lower is better).
    """
    try:
        # Temporarily save the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
            tmp_audio_file.write(recorded_audio.file.read())
            audio_path = tmp_audio_file.name

        # Sample sets of words by level
        level_vocabulary = {
            1: ["fish", "dog", "cat", "orange", "apple"],
            2: ["banana", "elephant", "dinosaur", "pineapple", "strawberry"],
        }
        vocabulary = level_vocabulary.get(level, level_vocabulary[1])
        test_words = vocabulary[:5]

        # OPTIONAL: Use text-to-speech in a separate thread so it doesn't conflict
        speak_in_thread(test_words)

        # Recognize the user's pronunciation from the audio sample
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            user_pronounced = recognizer.recognize_google(audio)

        # Convert words to IPA
        original_phonetics = " ".join([ipa.convert(word) for word in test_words])
        user_phonetics = ipa.convert(user_pronounced)

        # Calculate phonetics inaccuracy using Levenshtein distance
        distance = levenshtein(original_phonetics, user_phonetics)
        phonetics_inaccuracy = distance / max(len(original_phonetics), 1)

        # Cleanup
        os.remove(audio_path)

        return {
            "user_id": user_id,
            "test_words": test_words,
            "user_pronounced": user_pronounced,
            "phonetics_inaccuracy": round(phonetics_inaccuracy * 100, 2),  # as percentage
        }

    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand the audio.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing phonetics: {str(e)}")


import threading
import pyttsx3

def speak_text(text: str):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

def speak_in_thread(text: str):
    # Run TTS in a separate thread so it doesn't block or conflict with the event loop
    tts_thread = threading.Thread(target=speak_text, args=(text,))
    tts_thread.start()


#-----------------------------------------------------------------
# HELPER: Levenshtein Distance
#-----------------------------------------------------------------
def levenshtein(s1: str, s2: str) -> int:
    """
    Compute the Levenshtein distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s2:
        return len(s1)

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]