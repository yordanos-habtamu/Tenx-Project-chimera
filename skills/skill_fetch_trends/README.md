# Skill: Fetch Trends

## Purpose
Fetches trending topics from various platforms (Google Trends, YouTube, Twitter) and returns structured trend data.

## Category
Research

## Input Contract
```python
{
    "platform": str,  # "google_trends" | "youtube" | "twitter"
    "region": str,    # ISO country code (e.g., "US", "GB")
    "category": str,  # Optional category filter
    "limit": int      # Max number of trends to return (default: 10)
}
```

## Output Contract
```python
{
    "trends": [
        {
            "keyword": str,
            "volume": int,
            "timestamp": str,  # ISO 8601
            "related_queries": list[str],
            "sentiment_score": float  # -1.0 to 1.0
        }
    ],
    "metadata": {
        "platform": str,
        "fetched_at": str,
        "region": str
    }
}
```

## Dependencies
- `pytrends`: Google Trends API
- `tweepy`: Twitter API (optional)
- `google-api-python-client`: YouTube API (optional)

## Error Handling
- **RateLimitError**: Platform rate limit exceeded
- **AuthenticationError**: Invalid API credentials
- **NetworkError**: Connection failure

## Example Usage
```python
from skills.skill_fetch_trends import fetch_trends

result = fetch_trends({
    "platform": "google_trends",
    "region": "US",
    "limit": 10
})
```
