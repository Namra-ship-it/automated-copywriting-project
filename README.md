# ✍️ CopyAlchemist — Automated AI Copywriting System

> **AI-powered marketing copy generation with platform optimization, tone control, validation, asynchronous processing, retry handling, and batch generation.**

**CopyAlchemist** is a modular Python-based AI copywriting system that transforms structured product information into **platform-specific, audience-aware marketing content**.

The system integrates **Google Gemini** for content generation and combines it with Pydantic validation, configurable generation parameters, platform constraints, brand-safety checks, asynchronous processing, retry/backoff handling, structured logging, CLI workflows, and a Streamlit web interface.

---

## ✨ Overview

Creating marketing content for multiple platforms often requires repeatedly rewriting the same product information.

CopyAlchemist automates that workflow.

```text
Product Information
        │
        ▼
Request Validation
        │
        ▼
Prompt Construction
        │
        ▼
Async Generation
        │
        ▼
Google Gemini
        │
        ▼
Output Validation
        │
        ▼
Structured Marketing Copy
```

Provide:

* Product name
* Product description
* Target audience
* Marketing platform
* Desired tone
* Call-to-action
* Generation parameters

The system produces structured, platform-aware marketing copy ready for further use.

---

# 🚀 Key Features

### 🎯 Multi-Platform Generation

Generate marketing content tailored for:

* 💼 **LinkedIn**
* 📸 **Instagram**
* 📧 **Email**

Platform-specific rules can be applied during prompt construction and output validation.

---

### 🎨 Configurable Tone

CopyAlchemist supports multiple writing styles:

* Professional
* Casual
* Persuasive
* Humorous
* Inspirational
* Eco-conscious
* Adventurous

Tone is treated as a generation parameter rather than being hard-coded into the application.

---

### 🤖 Google Gemini Integration

The system uses Google's Gemini API for AI-powered copy generation.

The selected model is configurable through environment variables, allowing the model to be changed without modifying the core application logic.

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_model_here
```

---

### ⚡ Asynchronous Processing

Copy generation uses Python's asynchronous capabilities to process requests efficiently.

Configurable concurrency limits help control the number of simultaneous API requests.

```env
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=60
```

---

### 📦 Batch Generation

Generate content for multiple products from a JSON input file.

```bash
python src/cli.py --batch \
  --input-file examples/sample_inputs.json \
  --output-file outputs/batch/results.json
```

This makes the system suitable for larger product catalogs and campaign workflows.

---

### 🔄 Retry & Backoff

External APIs can experience temporary failures.

CopyAlchemist includes configurable resilience mechanisms:

* Retry attempts
* Exponential backoff
* Random jitter
* Request timeouts
* Concurrency control

Example configuration:

```env
RETRY_ATTEMPTS=3
BACKOFF_MULTIPLIER=2.0
JITTER_RANGE=0.1
```

---

### 🛡️ Validation & Brand Safety

Generated content is validated before being returned.

Validation can cover:

* Required fields
* Platform constraints
* Character limits
* Brand-safety rules
* Output structure
* Generation parameters

This provides an additional application-level quality and safety layer around AI-generated content.

---

### 📋 Strongly Typed Data Models

Requests and responses use **Pydantic models**.

This provides:

* Input validation
* Structured output
* Type safety
* Consistent error handling
* Machine-readable responses

---

### 🖥️ Multiple Interfaces

CopyAlchemist supports:

**CLI**

```bash
python src/cli.py --interactive
```

**Streamlit Web App**

```bash
streamlit run app.py
```

**Python API**

The core generation components can also be imported and used programmatically.

---

### 📝 Structured Logging

The application uses structured logging to make development, debugging, and runtime monitoring easier.

---

# 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │   CLI / Streamlit    │
                    │    / Python API      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     CopyRequest      │
                    │      Pydantic        │
                    │      Validation      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    PromptBuilder     │
                    │                      │
                    │ Platform + Tone +    │
                    │ Audience + CTA       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Async Handler     │
                    │                      │
                    │ Concurrency + Retry  │
                    │ + Backoff + Timeout  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Gemini API       │
                    │    AI Generation     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Copy Validator    │
                    │                      │
                    │ Platform + Brand +   │
                    │ Output Constraints   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    CopyResponse      │
                    │   Structured JSON    │
                    └──────────────────────┘
```

---

# 🧩 Project Structure

```text
CopyAlchemist_task-02_Namra-Malik/
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

### Core Modules

| Module              | Responsibility                                   |
| ------------------- | ------------------------------------------------ |
| `models.py`         | Pydantic request and response models             |
| `config.py`         | Application and environment configuration        |
| `prompt_builder.py` | Builds platform- and tone-aware prompts          |
| `generator.py`      | Handles Gemini content generation                |
| `async_handler.py`  | Async processing, concurrency and retry handling |
| `validators.py`     | Validates generated copy                         |
| `cli.py`            | Command-line interface                           |
| `main.py`           | Application entry point                          |
| `utils.py`          | Shared utility functionality                     |
| `app.py`            | Streamlit web interface                          |
| `tests/`            | Automated test suite                             |

---

# 🛠️ Technology Stack

| Technology       | Purpose                          |
| ---------------- | -------------------------------- |
| 🐍 Python        | Core application                 |
| 🤖 Google Gemini | AI copy generation               |
| 📦 Pydantic      | Data validation and typed models |
| ⚡ `asyncio`      | Asynchronous processing          |
| 🔄 Retry/Backoff | API resilience                   |
| 📝 Loguru        | Structured logging               |
| 🧪 Pytest        | Automated testing                |
| 📄 JSON          | Batch input/output               |
| 🔐 python-dotenv | Environment configuration        |
| 🎈 Streamlit     | Interactive web interface        |

---

# ⚙️ Installation

## Prerequisites

Make sure the following are installed:

* Python 3.10+
* pip
* A Google Gemini API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/Namra-ship-it/CopyAlchemist_task-02_Namra-Malik.git
cd CopyAlchemist_task-02_Namra-Malik
```

---

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

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Configuration

Create your environment file from the provided template.

### Windows

```powershell
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Then configure your environment:

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

> 🔐 **Never commit `.env` or expose your Gemini API key.**

---

# 🖥️ Streamlit Web Application

CopyAlchemist includes an interactive Streamlit interface.

Start the application with:

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal.

Open that URL in your browser to access the web interface.

---

# 💻 CLI Usage

## Interactive Mode

Run:

```bash
python src/cli.py --interactive
```

The interactive workflow allows you to provide copywriting parameters directly through the terminal.

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

Prepare a JSON file containing multiple requests:

```bash
python src/cli.py \
  --batch \
  --input-file examples/sample_inputs.json \
  --output-file outputs/batch/results.json
```

Batch processing is useful for:

* Product catalogs
* Marketing campaigns
* Multiple audience segments
* Large-scale content generation

---

# 🐍 Programmatic Usage

The generation system can also be used directly from Python:

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


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 📤 Structured Output

CopyAlchemist returns structured data rather than only raw generated text.

Example:

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

This makes the output suitable for both human use and downstream applications.

---

# 🧪 Testing

Run the complete test suite:

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

### Run a Specific Test

```bash
pytest tests/test_models.py -v
```

The test suite covers core application behavior including models, generation logic, validation, and supporting components.

---

# ⚙️ Configuration Reference

| Variable                  | Description                    | Example        |
| ------------------------- | ------------------------------ | -------------- |
| `GEMINI_API_KEY`          | Gemini authentication key      | `your_api_key` |
| `GEMINI_MODEL`            | Gemini model to use            | `your_model`   |
| `MAX_CONCURRENT_REQUESTS` | Maximum simultaneous requests  | `10`           |
| `REQUEST_TIMEOUT`         | API request timeout            | `60`           |
| `RETRY_ATTEMPTS`          | Number of retry attempts       | `3`            |
| `BACKOFF_MULTIPLIER`      | Retry backoff multiplier       | `2.0`          |
| `JITTER_RANGE`            | Random retry jitter            | `0.1`          |
| `DEFAULT_TEMPERATURE`     | Default generation temperature | `0.7`          |
| `DEFAULT_TOP_P`           | Default nucleus sampling value | `0.9`          |
| `DEFAULT_MAX_TOKENS`      | Maximum generated tokens       | `500`          |
| `LOG_LEVEL`               | Logging level                  | `INFO`         |

---

# 🛡️ Reliability & Safety

CopyAlchemist is designed to account for common problems associated with external AI APIs and generated content.

### API Reliability

* Configurable timeouts
* Retry attempts
* Exponential backoff
* Random jitter
* Concurrency limits

### Input Safety

* Pydantic request validation
* Strongly typed parameters
* Required-field validation

### Output Quality

* Platform constraint validation
* Character-limit validation
* Structured response validation
* Brand-safety checks

### Credential Security

API credentials are loaded through environment variables rather than being embedded in source code.

---

# 🎯 Design Principles

### 1. Platform-Aware Generation

Content should be adapted to its intended platform rather than treating every channel identically.

### 2. Structured AI Output

Generated content should be predictable and machine-readable.

### 3. Separation of Concerns

Generation, validation, configuration, prompt construction, and interface logic are separated into dedicated modules.

### 4. Resilient API Communication

External AI services can fail temporarily, so retries, backoff, timeouts, and concurrency controls are part of the architecture.

### 5. Configurable Behavior

Operational settings are controlled through environment variables rather than hard-coded application logic.

---

# 📈 Potential Extensions

The modular architecture allows the system to be extended with:

* Additional social platforms
* Brand voice profiles
* Multiple copy variations
* A/B testing
* SEO-focused generation
* Content history
* Database persistence
* Streaming generation
* Authentication
* User accounts
* Docker deployment
* CI/CD automation
* Production API deployment

---

# 🔐 Security Guidelines

Never commit:

```text
.env
API keys
credentials
private configuration
generated runtime secrets
```

Use:

```text
.env.example
```

for sharing configuration structure without exposing credentials.

If an API key is accidentally committed, **revoke and rotate it immediately**.

---

# 🤝 Contributing

Contributions and improvements are welcome.

Create a feature branch:

```bash
git checkout -b feature/your-feature
```

Make your changes, add or update tests where appropriate, and submit a pull request.

---

# 📌 Project Status

**Status:** Active educational / portfolio project

The core system provides AI generation, validation, asynchronous processing, batch workflows, CLI usage, and an interactive Streamlit interface.

---

# 👩‍💻 Author

**Namra Malik**

GitHub:
https://github.com/Namra-ship-it

---

# ⭐ Repository

**CopyAlchemist — Task 02**

https://github.com/Namra-ship-it/CopyAlchemist_task-02_Namra-Malik

If you find the project useful, consider giving it a ⭐ on GitHub.

---

## 📄 License

This project was developed as part of **Task 02** and is intended for educational, portfolio, and project-evaluation purposes.
