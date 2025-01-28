import cv2
import tempfile
import pyttsx3
import pytesseract
from textblob import TextBlob
import speech_recognition as sr

from abydos.phonetic import Soundex, Metaphone, Caverphone, NYSIIS

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from a handwriting sample using OCR.
    """
    image = cv2.imread(image_path)
    text = pytesseract.image_to_string(image)
    return text

def spelling_accuracy(text: str) -> float:
    """
    Calculate spelling accuracy based on TextBlob corrections.
    """
    corrected_text = str(TextBlob(text).correct())
    errors = levenshtein(text, corrected_text)
    return 100 * (1 - errors / max(len(text), 1))

def phonetic_accuracy(text: str) -> float:
    """
    Calculate phonetic accuracy using Soundex and other algorithms.
    """
    soundex = Soundex()
    metaphone = Metaphone()
    original_phonetics = [soundex.encode(word) for word in text.split()]
    corrected_text = str(TextBlob(text).correct())
    corrected_phonetics = [soundex.encode(word) for word in corrected_text.split()]
    errors = levenshtein(" ".join(original_phonetics), " ".join(corrected_phonetics))
    return 100 * (1 - errors / max(len(original_phonetics), 1))

def process_handwriting_analysis(image_path: str) -> dict:
    """
    Perform text analysis on extracted handwriting text.
    """
    text = extract_text_from_image(image_path)
    return {
        "text": text,
        "spelling_accuracy": spelling_accuracy(text),
        "phonetic_accuracy": phonetic_accuracy(text),
    }

def levenshtein(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]



def percentage_of_phonetic_accuraccy(extracted_text: str) -> float:
    """
    Calculate phonetic accuracy using Soundex, Metaphone, Caverphone, and NYSIIS.
    """
    soundex = Soundex()
    metaphone = Metaphone()
    caverphone = Caverphone()
    nysiis = NYSIIS()
    spell_corrected = TextBlob(extracted_text).correct()

    phonetics_scores = []

    for encoding in [soundex, metaphone, caverphone, nysiis]:
        original = " ".join([encoding.encode(word) for word in extracted_text.split()])
        corrected = " ".join([encoding.encode(word) for word in spell_corrected.split()])
        score = (len(original) - levenshtein(original, corrected)) / (len(original) + 1)
        phonetics_scores.append(score)

    return sum(phonetics_scores) / len(phonetics_scores) * 100