import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler

# Load the trained model
model = load_model("app/models/dyslexia_detection_model.h5")
print("Model loaded successfully.")

# Scaler
scaler = StandardScaler()

# Parameters
time_steps = 100
num_features = 4

# MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def extract_eye_tracking_data(frame):
    """Extract eye tracking data from a single video frame."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            left_eye = landmarks.landmark[33]  # Left eye center
            right_eye = landmarks.landmark[133]  # Right eye center

            h, w, _ = frame.shape
            LX = int(left_eye.x * w)
            LY = int(left_eye.y * h)
            RX = int(right_eye.x * w)
            RY = int(right_eye.y * h)

            return LX, LY, RX, RY

    # Return random values if no face is detected
    return np.random.random(), np.random.random(), np.random.random(), np.random.random()

def process_video_for_dyslexia(video_path):
    """Process the video to detect dyslexia using eye-tracking."""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Error: Could not open video {video_path}")

    sequence = []
    results = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        LX, LY, RX, RY = extract_eye_tracking_data(frame)
        sequence.append([LX, LY, RX, RY])

        if len(sequence) == time_steps:
            sequence_array = np.array(sequence).reshape(-1, num_features)
            sequence_array = scaler.fit_transform(sequence_array).reshape(1, time_steps, num_features)

            # Predict dyslexia probability
            prediction = model.predict(sequence_array)
            dyslexia_prob = prediction[0][0]
            results.append(dyslexia_prob)

            sequence = []  # Reset sequence for the next batch

    cap.release()
    return {
        "dyslexia_probability": np.mean(results),  # Average prediction across the video
        "frames_analyzed": len(results)
    }
