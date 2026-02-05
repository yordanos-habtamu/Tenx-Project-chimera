# Skill: Publish Content

## Purpose
Publishes video content to multiple platforms (YouTube, TikTok, Instagram) with proper metadata and scheduling.

## Category
Distribution

## Input Contract
```python
{
    "video": {
        "url": str,           # URL or local path to video
        "title": str,
        "description": str,
        "tags": list[str],
        "thumbnail_url": str  # Optional custom thumbnail
    },
    "platforms": list[str],   # ["youtube", "tiktok", "instagram"]
    "schedule": {
        "publish_at": str,    # ISO 8601 timestamp, None for immediate
        "timezone": str       # IANA timezone (e.g., "America/New_York")
    },
    "settings": {
        "visibility": str,    # "public" | "private" | "unlisted"
        "monetization": bool,
        "comments_enabled": bool,
        "restrict_age": bool
    }
}
```

## Output Contract
```python
{
    "results": [
        {
            "platform": str,
            "status": str,        # "published" | "scheduled" | "failed"
            "video_id": str,      # Platform-specific video ID
            "url": str,           # Public URL to video
            "published_at": str,
            "error": str          # Error message if failed
        }
    ],
    "metadata": {
        "total_platforms": int,
        "successful": int,
        "failed": int,
        "initiated_at": str
    }
}
```

## Dependencies
- `google-api-python-client`: YouTube Data API
- `instagrapi`: Instagram API
- `TikTokApi`: TikTok unofficial API

## Error Handling
- **AuthenticationError**: Invalid credentials for platform
- **UploadError**: File upload failed
- **ValidationError**: Content violates platform policies
- **QuotaError**: Daily upload limit reached

## Example Usage
```python
from skills.skill_publish_content import publish_content

result = publish_content({
    "video": {
        "url": "https://storage.example.com/video.mp4",
        "title": "10 AI Tools You Need to Try",
        "description": "Discover the best AI automation tools...",
        "tags": ["AI", "automation", "productivity"]
    },
    "platforms": ["youtube", "tiktok"],
    "schedule": {
        "publish_at": "2026-02-06T10:00:00Z",
        "timezone": "America/New_York"
    },
    "settings": {
        "visibility": "public",
        "monetization": True,
        "comments_enabled": True
    }
})
```
