import whisper


def transcribe(audio_path: str) -> str:
    model = whisper.load_model("turbo")
    result = model.transcribe(audio_path)
    return result["text"]