# 🧠 Dyslexia Detection API 🚀

🌟 **Empowering Education with Advanced AI Tools** 🌟

This repository contains the backend for the **Dyslexia Detection API** – a FastAPI-based solution designed to assist in dyslexia detection using advanced eye-tracking and audio analysis techniques.

---

## 🎯 Features

- 🔍 **Eye Tracking**: Uses video input to analyze gaze patterns and identify dyslexia indicators.
- 🎙️ **Audio Processing**: Extracts and evaluates speech during reading tasks.
- 📝 **Questionnaire Analysis**: Analyzes answers to targeted questions for further insights.
- 📊 **Detailed Reporting**: Generates a comprehensive report with a percentage probability of dyslexia.
- ⚡ **Optimized for Speed**: Leveraging concurrency and queues for fast processing.
- 🛠️ **Custom ML Models**: Built using TensorFlow, MediaPipe, and Scikit-learn.

---

## 🛠️ Installation

Follow these steps to set up the project locally:

1. Clone the repo:
   ```bash
   git clone https://github.com/edulex/dyslexia-detection-api.git
   ```
2. Navigate to the directory:
   ```bash
   cd dyslexia-detection-api
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 🎥 How It Works

1. 🌐 **Upload Video**: Send a video file containing the reading session via the `/detect` endpoint.
2. 🖥️ **Processing**:
   - Video: Eye-tracking analysis to monitor gaze patterns.
   - Audio: Extracted and analyzed for reading fluency.
3. 📝 **Questionnaire**: Results are evaluated for additional indicators.
4. 📈 **Report**: A detailed report is generated and stored.

---

## 🚀 API Endpoints

| Endpoint        | Method | Description                     |
| --------------- | ------ | ------------------------------- |
| `/detect`       | POST   | Upload video for analysis.      |
| `/results/{id}` | GET    | Retrieve analysis results.      |
| `/health-check` | GET    | Check if the server is running. |

---

## 🔧 Tech Stack

- 🌐 **FastAPI**: For blazing-fast backend APIs.
- 🧠 **TensorFlow**: For running the ML models.
- 🎥 **MediaPipe**: For real-time eye tracking.
- 🎙️ **MoviePy**: For audio extraction.
- 🐍 **Python**: The backbone of this project.

---

## 📂 Folder Structure

```plaintext
dyslexia-detection-api/
├── app/
│   ├── routers/        # API endpoints
│   ├── services/       # Core processing logic
│   ├── models/         # ML models
│   ├── utils/          # Helper functions
│   ├── main.py         # FastAPI entry point
├── tests/              # Unit tests
├── requirements.txt    # Project dependencies
├── README.md           # Project documentation
```

---

## 🛡️ License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

---

## 👩‍💻 Author

## **Edulex Team** ✨
