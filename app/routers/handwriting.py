from fastapi import APIRouter, UploadFile, HTTPException
from app.utils.text_analysis import process_handwriting_analysis
from app.services.handwriting_processing import process_handwriting_for_dyslexia
import os

router = APIRouter(prefix="/handwriting", tags=["Handwriting Analysis"])

UPLOAD_DIR = "app/data/uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analyze/")
async def analyze_handwriting(file: UploadFile):
    """
    Analyze a handwriting sample for dyslexia indicators.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    # Save the uploaded image
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    try:
        # Process handwriting features
        handwriting_features = process_handwriting_for_dyslexia(file_path)
        # Perform additional analysis for spelling and phonetic accuracy
        analysis_results = process_handwriting_analysis(file_path)
        return {
            "handwriting_features": handwriting_features,
            "text_analysis": analysis_results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
