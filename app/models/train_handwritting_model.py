import pytesseract
from textblob import TextBlob
from abydos.phonetic import Soundex


def extract_text_from_image(image):
    """
    Extract text using OCR with confidence checks.
    """
    custom_config = r'--oem 3 --psm 6'  # Tesseract settings
    data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
    text = " ".join(data['text']).strip()
    confidence = (
        sum([int(conf) for conf in data['conf'] if conf.isdigit()]) / len(data['conf'])
        if data['conf'] else 0
    )
    return text, confidence


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


def calculate_text_analysis(text):
    """
    Analyze text for spelling and phonetic accuracy.
    """
    corrected_text = str(TextBlob(text).correct())
    spelling_accuracy = 100 * (1 - levenshtein(text, corrected_text) / max(len(text), 1))

    # Phonetic accuracy
    soundex = Soundex()
    original_phonetics = [soundex.encode(word) for word in text.split()]
    corrected_phonetics = [soundex.encode(word) for word in corrected_text.split()]
    phonetic_accuracy = 100 * (1 - levenshtein(" ".join(original_phonetics), " ".join(corrected_phonetics)) /
                               max(len(original_phonetics), 1))

    return {
        "text": text,
        "spelling_accuracy": spelling_accuracy,
        "phonetic_accuracy": phonetic_accuracy,
    }
