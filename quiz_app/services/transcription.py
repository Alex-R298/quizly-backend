import whisper


def transcribe(audio_path: str) -> str:
    """Load the Whisper model and transcribe the audio file at the given path."""
    model = whisper.load_model("turbo")
    result = model.transcribe(audio_path)
    return result["text"]