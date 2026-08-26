# System Architecture

## Overview

The Automated Copywriting & Tone Transformer is a Python application that generates platform-optimized marketing copy using the DeepSeek API. It follows a layered architecture with clear separation of concerns.

## Architecture Flow

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
                                            │  DeepSeek API   │
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

## Concurrency Patterns

### Semaphore-Based Throttling
- `AsyncHandler` uses `asyncio.Semaphore` to limit concurrent API requests
- Default limit: 10 concurrent requests (configurable via `MAX_CONCURRENT_REQUESTS`)
- Prevents rate limiting and ensures stable throughput

### Batch Processing
- `BatchHandler` orchestrates multiple requests via `AsyncHandler`
- Uses `asyncio.gather()` with `return_exceptions=True` for error isolation
- Failed requests do not block successful ones

## Rate Limiting Strategy

1. **Client-Side Throttling**: Semaphore enforces max concurrency
2. **Exponential Backoff**: `delay = multiplier * 2^attempt ± jitter`
3. **Retry Logic**: Configurable attempts with tenacity decorators
4. **Error Isolation**: Exceptions caught per-request, not per-batch

## DeepSeek API Integration

- Uses OpenAI-compatible SDK (`openai>=1.0.0`)
- Custom `base_url` pointing to `https://api.deepseek.com/v1`
- JSON mode enforced via `response_format={"type": "json_object"}`
- Both sync (`OpenAI`) and async (`AsyncOpenAI`) clients maintained

## Error Handling Approach

| Layer | Strategy |
|-------|----------|
| Input | Pydantic validation with detailed error messages |
| API | Tenacity retry with exponential backoff |
| Parse | Try/except with fallback error responses |
| Output | Validator checks + auto-correction |
