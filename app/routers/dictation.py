from fastapi import APIRouter, Query, HTTPException
from typing import List

router = APIRouter(prefix="/dictation", tags=["Dictation"])

# Define age-based phrases
AGE_BASED_PHRASES = {
    "under_7": [
        "The cat is on the mat.",
        "I like my red ball.",
        "It is a sunny day.",
        "We go to the park.",
        "I love my dog."
    ],
    "under_14": [
        "The river flows through the valley.",
        "Science is an interesting subject.",
        "We learn new things every day.",
        "Teamwork helps us succeed.",
        "Reading books expands our knowledge."
    ],
    "under_21": [
        "The advancements in technology are remarkable.",
        "Environmental conservation is crucial for our planet.",
        "Education shapes the future of our society.",
        "Artificial intelligence is transforming industries.",
        "Climate change demands immediate attention."
    ]
}

@router.get("/phrases/")
async def get_dictation_phrases(age: int = Query(..., ge=0, le=21)):
    """
    Get age-appropriate phrases for dictation.

    Args:
        age (int): Age of the student. Should be between 0 and 21.

    Returns:
        List[str]: List of phrases suitable for dictation based on age.
    """
    if age < 7:
        phrases = AGE_BASED_PHRASES["under_7"]
    elif age < 14:
        phrases = AGE_BASED_PHRASES["under_14"]
    elif age <= 21:
        phrases = AGE_BASED_PHRASES["under_21"]
    else:
        raise HTTPException(status_code=400, detail="Age must be between 0 and 21.")

    return {"age": age, "phrases": phrases}
