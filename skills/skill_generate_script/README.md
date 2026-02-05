# Skill: Generate Script

## Purpose
Generates video scripts based on trend data and content requirements using AI (OpenRouter/GPT).

## Category
Content

## Input Contract
```python
{
    "trend": {
        "keyword": str,
        "context": str,  # Additional context about the trend
        "volume": int
    },
    "style": str,        # "educational" | "entertaining" | "informative"
    "duration": int,     # Target duration in seconds
    "tone": str,         # "casual" | "professional" | "humorous"
    "target_audience": str  # Optional audience description
}
```

## Output Contract
```python
{
    "script": {
        "title": str,
        "hook": str,         # First 5-10 seconds
        "body": str,         # Main content
        "call_to_action": str,  # CTA
        "estimated_duration": int,
        "keywords": list[str]
    },
    "metadata": {
        "model_used": str,
        "generated_at": str,
        "word_count": int,
        "reading_time_seconds": int
    }
}
```

## Dependencies
- `openai`: OpenRouter API client
- `tiktoken`: Token counting

## Error Handling
- **InvalidInputError**: Missing required fields
- **APIError**: AI service error
- **TokenLimitError**: Content too long for model

## Example Usage
```python
from skills.skill_generate_script import generate_script

result = generate_script({
    "trend": {
        "keyword": "AI Automation",
        "context": "Growing interest in AI tools",
        "volume": 50000
    },
    "style": "educational",
    "duration": 60,
    "tone": "professional"
})
```
