# Deployment Guide

## Environment Setup

### Requirements
- Python 3.10+
- DeepSeek API key
- 2GB RAM minimum
- Internet access for API calls

### Installation

```bash
# 1. Extract or clone the project
cd automated_copywriting_project

# 2. Run automated setup
bash scripts/setup.sh

# 3. Configure environment
cp .env.example .env
nano .env  # Add your DEEPSEEK_API_KEY
```

## Configuration

Edit `.env` with your settings:

```env
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_MODEL=deepseek-chat
MAX_CONCURRENT_REQUESTS=10
RETRY_ATTEMPTS=3
DEFAULT_TEMPERATURE=0.7
```

## Running in Production

### Real-Time Mode
```bash
python src/cli.py --product "X" --description "Y" --platform LinkedIn --tone Professional --audience "Z" --cta "Learn more"
```

### Batch Mode
```bash
python src/cli.py --batch --input-file data/requests.json --output-file data/results.json
```

### As a Module
```python
from src.batch_handler import BatchHandler
handler = BatchHandler()
handler.process_file("input.json", "output.json")
```

## Monitoring

### Logs
Application logs are written to `logs/app.log` with rotation:
- 10 MB per file
- 7-day retention

### Log Levels
Set `LOG_LEVEL=DEBUG` for verbose output, `INFO` for normal operation.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `DEEPSEEK_API_KEY not set` | Add API key to `.env` |
| `Rate limit exceeded` | Reduce `MAX_CONCURRENT_REQUESTS` |
| `JSON parse error` | Increase `MAX_TOKENS` or reduce `TEMPERATURE` |
| `Validation failed` | Check platform-specific rules in output |
| `Timeout` | Increase `REQUEST_TIMEOUT` in `.env` |

## Performance Tuning

- **High throughput**: Increase `MAX_CONCURRENT_REQUESTS` (max 50 recommended)
- **Cost reduction**: Lower `DEFAULT_MAX_TOKENS` and `DEFAULT_TEMPERATURE`
- **Better quality**: Use `temperature=0.5-0.8` for consistent results
- **Batch efficiency**: Process 100+ requests via `--batch` mode
