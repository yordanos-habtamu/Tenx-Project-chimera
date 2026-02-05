# Skill: Generate Video

## Purpose
Generates video content from a script using AI video generation APIs (e.g., Runway, Synthesia, or custom providers).

## Category
Content

## Input Contract
```python
{
    "script": {
        "title": str,
        "body": str,
        "duration": int
    },
    "video_style": str,   # "talking_head" | "animated" | "slideshow"
    "resolution": str,    # "720p" | "1080p" | "4k"
    "voice": {
        "gender": str,    # "male" | "female" | "neutral"
        "accent": str,    # "american" | "british" | "neutral"
        "speed": float    # 0.5 to 2.0
    },
    "background_music": bool,
    "subtitles": bool
}
```

## Output Contract
```python
{
    "video": {
        "url": str,           # URL to generated video
        "thumbnail_url": str,
        "duration": int,
        "file_size_mb": float,
        "resolution": str,
        "format": str         # "mp4" | "webm"
    },
    "status": str,            # "completed" | "processing" | "failed"
    "metadata": {
        "generated_at": str,
        "provider": str,
        "job_id": str,
        "cost_estimate": float  # USD
    }
}
```

## Dependencies
- `requests`: API calls
- `aiohttp`: Async API polling

## Error Handling
- **ProcessingError**: Video generation failed
- **TimeoutError**: Generation took too long
- **QuotaExceededError**: API quota exceeded

## Example Usage
```python
from skills.skill_generate_video import generate_video

result = generate_video({
    "script": {
        "title": "AI Automation Guide",
        "body": script_content,
        "duration": 60
    },
    "video_style": "talking_head",
    "resolution": "1080p",
    "voice": {
        "gender": "neutral",
        "accent": "american",
        "speed": 1.0
    },
    "subtitles": True
})
```
