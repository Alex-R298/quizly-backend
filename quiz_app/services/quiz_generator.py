from .youtube import download_audio
from .transcription import transcribe
from .llm import generate_questions


def generate_quiz_from_url(url: str) -> dict:
    audio_path = download_audio(url)
    try:
        text = transcribe(str(audio_path))          
        quiz = generate_questions(text)
        quiz["video_url"] = url
        return quiz
    finally:
        audio_path.unlink(missing_ok=True)