import tempfile
import os
import eng_to_ipa as ipa
from app.utils.levenshtein import levenshtein
import speech_recognition as sr

def analyze_phonetics(user_id: str, recorded_audio_path: str, level: int):
    """
    Analyze the user's pronunciation by comparing it to a predefined set of words.
    Returns a phonetics inaccuracy score (lower is better).
    """
    try:
        # Predefined vocabulary sets
        level_vocabulary = {
            1: ["fish", "dog", "cat", "orange", "apple"],
            2: ["banana", "elephant", "dinosaur", "pineapple", "strawberry"],
        }
        vocabulary = level_vocabulary.get(level, level_vocabulary[1])
        test_words = vocabulary[:5]

        # Recognize the user's pronunciation from the audio sample
        recognizer = sr.Recognizer()
        with sr.AudioFile(recorded_audio_path) as source:
            audio = recognizer.record(source)
            user_pronounced = recognizer.recognize_google(audio)

        # Convert words to IPA
        original_phonetics = " ".join([ipa.convert(word) for word in test_words])
        user_phonetics = ipa.convert(user_pronounced)

        # Calculate phonetics inaccuracy using Levenshtein distance
        distance = levenshtein(original_phonetics, user_phonetics)
        phonetics_inaccuracy = distance / max(len(original_phonetics), 1)

        return {
            "test_words": test_words,
            "user_pronounced": user_pronounced,
            "phonetics_inaccuracy": round(phonetics_inaccuracy * 100, 2),  # as percentage
        }
    except sr.UnknownValueError:
        return {"error": "Could not understand the audio."}
    except Exception as e:
        return {"error": f"Error analyzing phonetics: {str(e)}"}
    

from pydub import AudioSegment
from fastapi import HTTPException
import os
from app.utils.levenshtein import levenshtein
import speech_recognition as sr
import eng_to_ipa as ipa


def convert_audio_to_wav(input_audio_path: str, output_audio_path: str):
    """
    Convert the input audio file to WAV format using pydub.

    Args:
        input_audio_path (str): Path to the input audio file.
        output_audio_path (str): Path to save the converted WAV file.

    Raises:
        HTTPException: If the audio conversion fails.
    """
    try:
        audio = AudioSegment.from_file(input_audio_path)
        audio.export(output_audio_path, format="wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting audio: {str(e)}")


def process_audio_for_phonetics(audio_path: str, test_words: list):
    """
    Process the audio for phonetics analysis by comparing pronunciation to test words.
    """
    wav_audio_path = audio_path
    if not audio_path.endswith(".wav"):
        wav_audio_path = os.path.splitext(audio_path)[0] + ".wav"
        convert_audio_to_wav(audio_path, wav_audio_path)

    # Enhance audio quality
    enhanced_audio_path = enhance_audio(wav_audio_path)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(enhanced_audio_path) as source:
            audio = recognizer.record(source)
            user_pronounced = recognizer.recognize_google(audio)

        # Convert words to IPA
        original_phonetics = " ".join([ipa.convert(word) for word in test_words])
        user_phonetics = ipa.convert(user_pronounced)

        # Calculate phonetics inaccuracy
        distance = levenshtein(original_phonetics, user_phonetics)
        max_length = max(len(original_phonetics), len(user_phonetics), 1)  # Avoid division by zero
        phonetics_inaccuracy = (distance / max_length) * 100  # Convert to percentage

        return {
            "test_words": test_words,
            "user_pronounced": user_pronounced,
            "phonetics_inaccuracy": round(phonetics_inaccuracy, 2),  # Round to 2 decimal places
        }
    except sr.UnknownValueError:
        return {"error": "Could not understand the audio."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing phonetics: {str(e)}")
    finally:
        # Clean up temporary files
        if enhanced_audio_path != wav_audio_path:
            os.remove(enhanced_audio_path)
