# Quizly – Backend

Quizly is a Django REST API that automatically generates quizzes from YouTube videos. A user submits a YouTube URL, the audio is downloaded and transcribed locally, and an AI generates 10 multiple-choice questions from the transcript.

## How It Works

1. User submits a YouTube URL via the API
2. Audio is downloaded using **yt-dlp**
3. **Whisper AI** transcribes the audio locally (no external API needed)
4. **Gemini Flash** generates 10 multiple-choice questions from the transcript
5. The quiz is saved and returned to the frontend

## Requirements

### FFmpeg (required)

Whisper AI requires FFmpeg to process audio files. FFmpeg must be installed **globally** and available in your system PATH.

**Windows:**
```bash
winget install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### Gemini API Key

Quiz generation uses the Gemini Flash model, which is free to use. Get your API key at:  
https://aistudio.google.com/app/apikey

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/Alex-R298/quizly-backend.git
cd quizly-backend

# 2. Create and activate a virtual environment
python -m venv env
env\Scripts\activate        # Windows
source env/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in the project root
GEMINI_API_KEY=your_api_key_here

# 5. Apply migrations
python manage.py migrate

# 6. Start the development server
python manage.py runserver
```

## Authentication

Authentication uses **JWT tokens** stored as **HTTP-only cookies**. After login, an `access_token` and a `refresh_token` are set as cookies and sent automatically with every request. The access token can be refreshed without re-login.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Register a new user account |
| POST | `/api/login/` | Log in and receive JWT cookies |
| POST | `/api/logout/` | Log out and clear JWT cookies |
| POST | `/api/token/refresh/` | Refresh the access token |
| GET | `/api/quizzes/` | List all quizzes of the authenticated user |
| POST | `/api/quizzes/` | Create a new quiz from a YouTube URL |
| GET | `/api/quizzes/{id}/` | Retrieve a specific quiz |
| PATCH | `/api/quizzes/{id}/` | Partially update a quiz title or description |
| DELETE | `/api/quizzes/{id}/` | Permanently delete a quiz |

## Tech Stack

| Technology | Purpose |
|---|---|
| Django | Web framework |
| Django REST Framework | REST API |
| SimpleJWT | JWT authentication |
| yt-dlp | YouTube audio download |
| Whisper AI | Local speech-to-text transcription |
| Gemini Flash | AI-powered quiz generation |
| SQLite | Database (development) |
