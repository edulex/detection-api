from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models import SessionLocal
from app.db.crud import get_queued_tasks, update_task_status
from app.services.video_processing import process_video_for_dyslexia
from app.utils.levenshtein import levenshtein
import requests
import os
import speech_recognition as sr
import eng_to_ipa as ipa
import tempfile
from pydub import AudioSegment

router = APIRouter(prefix="/process", tags=["Task Processing"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def convert_audio_to_wav(audio_path: str) -> str:
    """
    Convert any audio format to WAV.
    Returns the path of the converted WAV file.
    """
    wav_audio_path = os.path.splitext(audio_path)[0] + ".wav"
    
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(16000)  # Convert to mono and 16kHz for better recognition
        audio.export(wav_audio_path, format="wav")
        return wav_audio_path
    except Exception as e:
        raise Exception(f"Error converting audio: {str(e)}")

def process_audio_for_phonetics(audio_path: str, test_words: list):
    """
    Process the extracted audio for phonetic accuracy.
    """
    if not audio_path.endswith(".wav"):
        audio_path = convert_audio_to_wav(audio_path)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            user_pronounced = recognizer.recognize_google(audio)

        # Convert words to IPA for comparison
        original_phonetics = " ".join([ipa.convert(word) for word in test_words])
        user_phonetics = ipa.convert(user_pronounced)

        # Compute phonetics accuracy
        distance = levenshtein(original_phonetics, user_phonetics)
        max_length = max(len(original_phonetics), len(user_phonetics), 1)
        phonetics_inaccuracy = (distance / max_length) * 100  # Convert to percentage

        return {
            "test_words": test_words,
            "user_pronounced": user_pronounced,
            "phonetics_inaccuracy": round(phonetics_inaccuracy, 2),
        }
    except sr.UnknownValueError:
        return {"error": "Could not understand the audio."}
    except Exception as e:
        return {"error": f"Error analyzing phonetics: {str(e)}"}

def process_handwriting_with_api(handwriting_image_path: str):
    """
    Sends handwriting image to the external handwriting classification API.
    """
    try:
        with open(handwriting_image_path, "rb") as img:
            response = requests.post("https://api.athul.live/classify-page/", files={"file": img})

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to process handwriting. Status: {response.status_code}, Message: {response.text}"}
    except Exception as e:
        return {"error": f"Error processing handwriting: {str(e)}"}

@router.post("/")
async def process_tasks(db: Session = Depends(get_db)):
    """
    Process all tasks in the 'queued' state.
    """
    tasks = get_queued_tasks(db)
    results = {}

    for task in tasks:
        try:
            # Mark task as processing
            update_task_status(db, task.id, "processing")

            # Initialize result storage
            result = {}

            # Process video analysis (eye tracking)
            if task.video_path:
                video_result = process_video_for_dyslexia(task.video_path)
                result["video_analysis"] = video_result

            # Process phonetics using extracted audio
            if task.audio_path:
                test_words = ["The", "cat", "is", "on", "the", "mat", "The", "dog", "runs", "fast", "Look", "at", "the", "ball", "Can", "you", "find", "all", "star"]  # Default test words
                phonetics_result = process_audio_for_phonetics(task.audio_path, test_words)
                result["phonetics_analysis"] = phonetics_result

            # Process handwriting analysis via external API
            if task.handwriting_image_path:
                handwriting_result = process_handwriting_with_api(task.handwriting_image_path)
                result["handwriting_analysis"] = handwriting_result

            # Mark task as completed with results
            update_task_status(db, task.id, "completed", result=str(result))
            results[task.id] = "completed"
        except Exception as e:
            # Mark task as failed with error details
            update_task_status(db, task.id, "failed", result=str(e))
            results[task.id] = f"failed: {str(e)}"

    return {"message": "Processing completed.", "results": results}
