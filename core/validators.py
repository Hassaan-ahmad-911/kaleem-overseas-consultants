import re
from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError

MAX_OFFER_VIDEO_MB = 50
YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def validate_video_size(file):
    if file and file.size > MAX_OFFER_VIDEO_MB * 1024 * 1024:
        raise ValidationError(f"Video must be smaller than {MAX_OFFER_VIDEO_MB} MB. Compress it, or upload it to YouTube and paste the link instead.")


def youtube_video_id(url):
    """Return the 11-character video id from a youtube.com/watch?v=, youtu.be/ or youtube.com/shorts/ link, or None."""
    if not url:
        return None
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower().removeprefix("www.").removeprefix("m.")
    parts = [part for part in parsed.path.split("/") if part]
    video_id = None
    if host == "youtu.be" and parts:
        video_id = parts[0]
    elif host in {"youtube.com", "youtube-nocookie.com"}:
        if parts[:1] == ["watch"]:
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            video_id = parts[1]
    return video_id if video_id and YOUTUBE_ID.match(video_id) else None
