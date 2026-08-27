<<<<<<< HEAD
# Automated Copywriting & Tone Transformer

A production-ready Python application that automatically generates professional, platform-optimized marketing copy using the DeepSeek API. Transform raw product descriptions into tailored content for LinkedIn, Instagram, and Email with controllable tone, temperature, and creativity.

---

## Features

- **Multi-Platform Support**: Generate copy optimized for LinkedIn, Instagram, and Email
- **Tone Control**: Professional, Casual, Persuasive, Humorous, Inspirational, Eco-conscious, Adventurous
- **Gemini AI Integration**: Powered by Gemini's advanced language models via OpenAI-compatible API
- **Async Processing**: Handle multiple requests concurrently with configurable semaphore limits
- **Batch Processing**: Process hundreds of requests from JSON input files
- **Exponential Backoff**: Intelligent retry logic with jitter for resilient API calls
- **Pydantic Validation**: Strict input/output validation with detailed error reporting
- **Brand Safety**: Enforced guidelines prevent exaggerated claims and inappropriate content
- **CLI Interface**: Interactive, real-time, and batch modes via command-line
- **Comprehensive Logging**: Structured logging with Loguru for all operations

---

## Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   CLI /     │────▶│  CopyRequest    │────▶│ PromptBuilder   │
│  Batch JSON │     │  (Pydantic)     │     │  (Template +    │
└─────────────┘     └─────────────────┘     │  Platform Rules)│
                                            └────────┬────────┘
                                                     │
                                            ┌────────▼────────┐
                                            │  AsyncHandler   │
                                            │  (Semaphore +   │
                                            │   Backoff)      │
                                            └────────┬────────┘
                                                     │
                                            ┌────────▼────────┐
                                            │  Gemini API   │
                                            │  (OpenAI SDK)   │
                                            └────────┬────────┘
                                                     │
                                            ┌────────▼────────┐
                                            │  CopyValidator  │
                                            │  (Platform +    │
                                            │   Brand Rules)  │
                                            └────────┬────────┘
                                                     │
                                            ┌────────▼────────┐
                                            │  CopyResponse   │
                                            │  (JSON Output)  │
                                            └─────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.10+
- Gemini API key

### Quick Setup

```bash
# Clone or extract the project
cd automated_copywriting_project

# Run the setup script
bash scripts/setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key | *(required)* |
| `GEMINI_BASE_URL` | Gemini API endpoint | 
| `GEMINI_MODEL` | Model to use | `Gemini-chat` |
| `MAX_CONCURRENT_REQUESTS` | Async semaphore limit | `10` |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | `60` |
| `RETRY_ATTEMPTS` | Number of retry attempts | `3` |
| `BACKOFF_MULTIPLIER` | Exponential backoff base | `2.0` |
| `JITTER_RANGE` | Random jitter range | `0.1` |
| `DEFAULT_TEMPERATURE` | Default creativity level | `0.7` |
| `DEFAULT_TOP_P` | Default nucleus sampling | `0.9` |
| `DEFAULT_MAX_TOKENS` | Default token limit | `500` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## Usage

### Interactive Mode

```bash
python src/cli.py --interactive
```

### Real-Time Single Request

```bash
python src/cli.py \
  --product "EcoCharge Pro" \
  --description "A portable solar power bank with 20000mAh capacity, waterproof, and built-in LED flashlight" \
  --platform Instagram \
  --tone "Eco-conscious" \
  --audience "Outdoor enthusiasts and eco-friendly travelers" \
  --cta "Shop now and go green" \
  --temperature 0.8 \
  --top-p 0.9
```

### Batch Processing

```bash
# From a JSON file
python src/cli.py --batch --input-file examples/sample_inputs.json --output-file outputs/batch/results.json

# Or use the batch script
bash scripts/run_batch.sh
```

### Programmatic Usage

```python
import asyncio
from src.models import CopyRequest, Platform, Tone
from src.generator import CopyGenerator

async def main():
    request = CopyRequest(
        product_name="EcoCharge Pro",
        product_description="Portable solar power bank...",
        platform=Platform.INSTAGRAM,
        tone=Tone.ECO_CONSCIOUS,
        target_audience="Outdoor enthusiasts",
        character_limit=2200,
        call_to_action="Shop now and go green",
        temperature=0.8,
        top_p=0.9,
    )

    generator = CopyGenerator()
    response = await generator.generate_async(request)
    print(response.copy)

asyncio.run(main())
```

---

## Output Format

All responses follow this JSON schema:

```json
{
  "platform": "Instagram",
  "tone_used": "Eco-conscious",
  "temperature_used": 0.8,
  "top_p_used": 0.9,
  "character_count": 450,
  "copy": "Your generated marketing copy here...",
  "subject_line": null,
  "hashtags": ["#EcoFriendly", "#SolarPower", "#OutdoorLife"],
  "validation_passed": true,
  "validation_errors": [],
  "model_used": "deepseek-chat"
}
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_models.py -v
```

---

## Project Structure

```
automated_copywriting_project/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry points and orchestration
│   ├── cli.py           # Command-line interface
│   ├── config.py        # Configuration management
│   ├── models.py        # Pydantic data models
│   ├── prompt_builder.py # Prompt template engine
│   ├── generator.py     # Gemini API integration
│   ├── async_handler.py # Concurrency & retry logic
│   ├── batch_handler.py # Batch processing orchestrator
│   ├── validator.py     # Output validation & brand safety
│   └── utils.py         # Utility functions
├── prompts/
│   ├── master_template.txt
│   ├── platform_instructions.json
│   └── brand_guidelines.txt
├── tests/               # Pytest test suite
├── examples/            # Sample inputs per platform
├── outputs/             # Generated results
├── logs/                # Application logs
├── scripts/             # Shell scripts for common tasks
└── docs/                # Architecture & deployment docs
```

---

## License

MIT License - See LICENSE file for details.

---

## Support

For issues, questions, or contributions, please refer to the project documentation in `docs/` or open an issue on the project repository.
=======
# automated-copywriting-project
>>>>>>> bb3bad61115652f2d8aab5bde4efc9d476cd5062
