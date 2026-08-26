# API Reference

## Classes

### `CopyRequest` (Pydantic Model)
Input model for copy generation.

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `product_name` | str | Yes | 1-200 chars |
| `product_description` | str | Yes | 10-2000 chars |
| `platform` | Platform | Yes | LinkedIn, Instagram, Email |
| `tone` | Tone | Yes | Enum value |
| `target_audience` | str | Yes | 1-500 chars |
| `character_limit` | int | No | 50-5000 (default: 3000) |
| `call_to_action` | str | Yes | 1-200 chars |
| `temperature` | float | No | 0.0-2.0 (default: 0.7) |
| `top_p` | float | No | 0.0-1.0 (default: 0.9) |
| `max_tokens` | int | No | 50-4000 (default: 500) |

### `CopyResponse` (Pydantic Model)
Output model for generated copy.

| Field | Type | Description |
|-------|------|-------------|
| `platform` | Platform | Target platform |
| `tone_used` | Tone | Applied tone |
| `temperature_used` | float | Temperature setting |
| `top_p_used` | float | Top_P setting |
| `character_count` | int | Exact copy length |
| `copy` | str | Generated text |
| `subject_line` | str \| None | Email subject (Email only) |
| `hashtags` | list[str] | Instagram hashtags (Instagram only) |
| `validation_passed` | bool | Validation status |
| `validation_errors` | list[str] | Error messages |
| `model_used` | str | DeepSeek model name |

### `CopyGenerator`
Generates copy via DeepSeek API.

**Methods:**
- `generate_async(request: CopyRequest) -> CopyResponse` — Async with retry
- `generate_sync(request: CopyRequest) -> CopyResponse` — Synchronous
- `generate_batch(requests, max_concurrent) -> list[CopyResponse]` — Batch async

### `AsyncHandler`
Manages async concurrency and retries.

**Methods:**
- `process_request_with_retry(coro, request_id) -> T` — Single request with backoff
- `process_batch(coros, request_ids) -> list[T | Exception]` — Batch with gather
- `stream_results(coros, request_ids)` — Yields results as they complete

### `BatchHandler`
Orchestrates batch processing from files.

**Methods:**
- `run_batch(requests) -> list[CopyResponse]` — Process list of requests
- `process_file(input_file, output_file) -> Path` — End-to-end file processing
- `load_batch_inputs(input_file) -> list[CopyRequest]` — Load and validate JSON

### `CopyValidator`
Validates output against platform and brand rules.

**Methods:**
- `validate(response, request) -> CopyResponse` — Full validation with auto-correction
- `validate_character_limit(text, limit) -> tuple[bool, int]` — Length check

### `PromptBuilder`
Compiles prompts from templates.

**Methods:**
- `build(request: CopyRequest) -> str` — Compile final prompt
- `reload() -> None` — Hot-reload templates from disk

## CLI Usage

```bash
# Interactive mode
python src/cli.py --interactive

# Real-time
python src/cli.py --product "X" --description "Y" --platform LinkedIn --tone Professional --audience "Z" --cta "Click"

# Batch
python src/cli.py --batch --input-file inputs.json --output-file results.json

# Validate config
python src/cli.py --validate-config
```
