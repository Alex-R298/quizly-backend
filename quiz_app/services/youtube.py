import tempfile
import uuid
from pathlib import Path

import yt_dlp


def download_audio(url: str) -> Path:
    tmp_dir = Path(tempfile.gettempdir())
    tmp_filename = str(tmp_dir / f"quizly_{uuid.uuid4().hex}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return Path(ydl.prepare_filename(info))


def fetch_metadata(url: str) -> dict:
    with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", ""),
            "description": info.get("description", ""),
        }