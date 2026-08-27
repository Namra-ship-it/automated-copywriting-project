# ✍️ Automated Copywriting & Tone Transformer

> **AI-powered marketing copy generation with platform optimization, tone control, validation, async processing, and batch generation.**

An intelligent Python-based copywriting system that transforms raw product information into **platform-specific, audience-aware marketing content**.

The system uses Google's Gemini API to generate copy for platforms such as **LinkedIn, Instagram, and Email**, while applying configurable tones, character limits, CTAs, brand-safety rules, validation, retry handling, and structured output.

---

## 🚀 What It Does

Instead of manually rewriting the same product description for every platform, this system automates the process:

```text
Product Information
        ↓
Request Validation
        ↓
Prompt Construction
        ↓
Gemini AI Generation
        ↓
Platform & Brand Validation
        ↓
Structured Marketing Copy
```

Give it:

* Product name
* Product description
* Target audience
* Platform
* Tone
* CTA
* Generation parameters

And it produces ready-to-use marketing copy.

---

## ✨ Key Features

### 🎯 Multi-Platform Copy Generation

Generate content optimized for:

* 💼 LinkedIn
* 📸 Instagram
* 📧 Email

Each platform can apply its own formatting and content requirements.

### 🎨 Tone Control

Supported tones include:

* Professional
* Casual
* Persuasive
* Humorous
* Inspirational
* Eco-conscious
* Adventurous

### 🤖 Gemini AI Integration

Uses Google's Gemini models for AI-powered content generation.

The model can be configured through environment variables, making it easy to switch models without modifying the application logic.

### ⚡ Asynchronous Processing

Uses asynchronous request handling with configurable concurrency limits.

This allows multiple copy-generation requests to be processed efficiently without blocking the application.

### 📦 Batch Processing

Generate copy for large numbers of products from JSON input files.

```bash
python src/cli.py --batch \
  --input-file examples/sample_inputs.json \
  --output-file outputs/batch/results.json
```

### 🔄 Retry & Backoff

API failures are handled using:

* Configurable retry attempts
* Exponential backoff
* Random jitter
* Request timeouts
* Concurrency control

This makes API communication more resilient.

### 🛡️ Brand Safety & Validation

Generated content is validated before being returned.

Validation can check:

* Platform constraints
* Character limits
* Required fields
* Brand-safety rules
* Output structure
* Generation parameters

### 📋 Pydantic Validation

Requests and responses use strongly typed Pydantic models.

This provides structured data validation and clearer error handling.

### 🖥️ CLI Interface

Supports:

* Interactive generation
* Single-request generation
* Batch processing

### 📝 Structured Logging

The project uses structured logging to make debugging and monitoring easier.

---

# 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │     CLI / JSON       │
                    │      Input           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    CopyRequest       │
                    │      Pydantic        │
                    │     Validation       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    PromptBuilder     │
                    │ Platform + Tone +    │
                    │ Audience + CTA Rules │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Async Handler      │
                    │ Concurrency + Retry  │
                    │   + Backoff          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Gemini API      │
                    │    AI Generation     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Copy Validator     │
                    │ Platform + Brand     │
                    │      Rules           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    CopyResponse      │
                    │   Structured JSON    │
                    └──────────────────────┘
```

---

# 🛠️ Tech Stack

| Technology       | Purpose                   |
| ---------------- | ------------------------- |
| 🐍 Python        | Core application          |
| 🤖 Google Gemini | AI copy generation        |
| 📦 Pydantic      | Data validation           |
| ⚡ asyncio        | Asynchronous processing   |
| 🔄 Retry/Backoff | API resilience            |
| 📝 Loguru        | Logging                   |
| 🧪 Pytest        | Testing                   |
| 📄 JSON          | Batch input/output        |
| 🔐 python-dotenv | Environment configuration |

---

# 📁 Project Structure

```text
automated-copywriting-project/
│
├── docs/
│
├── examples/
│   └── sample_inputs.json
│
├── logs/
│
├── outputs/
│
├── prompts/
│
├── scripts/
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── config.py
│   ├── models.py
│   ├── prompt_builder.py
│   ├── generator.py
│   ├── async_handler.py
│   ├── validators.py
│   └── utils.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── app.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Namra-ship-it/automated-copywriting-project.git

cd automated-copywriting-project
```

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv venv

venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```
## 🖥️ Streamlit Web App

The project also includes a Streamlit-based web interface for an interactive copywriting experience.

Run the application with:

```bash
streamlit run app.py
```

Then open the local URL provided by Streamlit in your browser. 🚀

---

# ▶️ Usage


## 4. Configure Environment Variables

Copy the example environment file:

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Then add your Gemini API configuration:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_model_here

MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=60
RETRY_ATTEMPTS=3

BACKOFF_MULTIPLIER=2.0
JITTER_RANGE=0.1

DEFAULT_TEMPERATURE=0.7
DEFAULT_TOP_P=0.9
DEFAULT_MAX_TOKENS=500

LOG_LEVEL=INFO
```

> ⚠️ Never commit your `.env` file or expose your API key publicly.

---

# ▶️ Usage

## Interactive Mode

```bash
python src/cli.py --interactive
```

This allows you to provide copywriting parameters interactively.

---

## Single Request

Example:

```bash
python src/cli.py \
  --product "EcoCharge Pro" \
  --description "A portable solar power bank with 20000mAh capacity, waterproof design, and built-in LED flashlight" \
  --platform Instagram \
  --tone "Eco-conscious" \
  --audience "Outdoor enthusiasts and eco-friendly travelers" \
  --cta "Shop now and go green"
```

---

## Batch Processing

Prepare a JSON file containing multiple copywriting requests:

```bash
python src/cli.py \
  --batch \
  --input-file examples/sample_inputs.json \
  --output-file outputs/batch/results.json
```

This is useful when generating content for large product catalogs or marketing campaigns.

---

# 🧩 Programmatic Usage

The generator can also be used directly from Python:

```python
import asyncio

from src.models import CopyRequest, Platform, Tone
from src.generator import CopyGenerator


async def main():

    request = CopyRequest(
        product_name="EcoCharge Pro",
        product_description=(
            "Portable solar power bank with 20000mAh capacity"
        ),
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

# 📤 Example Output

The application returns structured data rather than unstructured text:

```json
{
  "platform": "Instagram",
  "tone_used": "Eco-conscious",
  "temperature_used": 0.8,
  "top_p_used": 0.9,
  "character_count": 450,
  "copy": "Power your adventures with cleaner energy...",
  "subject_line": null,
  "hashtags": [
    "#EcoFriendly",
    "#SolarPower",
    "#OutdoorLife"
  ],
  "validation_passed": true,
  "validation_errors": [],
  "model_used": "gemini"
}
```

---

# 🧪 Testing

Run the complete test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

Run a specific test:

```bash
pytest tests/test_models.py -v
```

---

# 🔧 Configuration

The application is designed to keep operational settings outside the source code.

| Variable                  | Purpose                       |
| ------------------------- | ----------------------------- |
| `GEMINI_API_KEY`          | Gemini authentication         |
| `GEMINI_MODEL`            | Gemini model selection        |
| `MAX_CONCURRENT_REQUESTS` | Maximum simultaneous requests |
| `REQUEST_TIMEOUT`         | API timeout                   |
| `RETRY_ATTEMPTS`          | Number of retries             |
| `BACKOFF_MULTIPLIER`      | Retry backoff multiplier      |
| `JITTER_RANGE`            | Retry jitter                  |
| `DEFAULT_TEMPERATURE`     | Generation creativity         |
| `DEFAULT_TOP_P`           | Nucleus sampling              |
| `DEFAULT_MAX_TOKENS`      | Maximum generated tokens      |
| `LOG_LEVEL`               | Logging verbosity             |

---

# 🎯 Design Goals

The project was built around several principles:

**1. Structured generation**

AI output should be predictable and machine-readable.

**2. Platform awareness**

Marketing copy should not be generated as one generic block and reused everywhere.

**3. Reliability**

External AI APIs can fail, so retry and timeout mechanisms are built into the generation pipeline.

**4. Validation**

Generated text should pass application-level checks before being returned.

**5. Scalability**

Batch processing and asynchronous execution allow the system to handle multiple generation requests efficiently.

---

# 🔮 Future Improvements

Potential next steps include:

* [ ] Web-based dashboard
* [ ] More social platforms
* [ ] Brand voice profiles
* [ ] Multiple copy variations per request
* [ ] A/B testing support
* [ ] SEO-focused generation
* [ ] Content history
* [ ] Database persistence
* [ ] Streaming generation
* [ ] Authentication & user accounts
* [ ] Docker deployment
* [ ] CI/CD pipeline
* [ ] Production API deployment

---

# 🤝 Contributing

Contributions are welcome.

```bash
git checkout -b feature/your-feature
```

Make your changes, add tests where appropriate, and submit a pull request.

---

# 📄 License

This project is currently intended as an educational and portfolio project.

See the repository for the latest licensing information.

---

# 👩‍💻 Author

**Namra Malik**

GitHub:
https://github.com/Namra-ship-it

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub.

**Repository:**
https://github.com/Namra-ship-it/automated-copywriting-project
