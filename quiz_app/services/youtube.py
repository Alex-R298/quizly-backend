import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import yt_dlp


def extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from a standard or short URL."""
    parsed = urlparse(url)
    if parsed.hostname in ('youtu.be',):
        return parsed.path.lstrip('/')
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
        if parsed.path.startswith('/shorts/'):
            return parsed.path.split('/shorts/')[1]
    return None


def normalize_url(url: str) -> str:
    """Convert any supported YouTube URL to the canonical watch URL format."""
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {url}")
    return f"https://www.youtube.com/watch?v={video_id}"


def download_audio(url: str) -> Path:
    """Download the best available audio track from a YouTube URL to a temp file."""
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

