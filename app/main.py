from fastapi import FastAPI
from app.routers import detect, queue, process

app = FastAPI(
    title="Dyslexia Detection API",
    description="API for detecting dyslexia using video, audio, and questionnaires.",
    version="1.0.0"
)

# Include routers
app.include_router(detect.router)
app.include_router(queue.router)
app.include_router(process.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Dyslexia Detection API!"}
