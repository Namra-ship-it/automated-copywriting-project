"""Gemini API integration with sync/async generation and retry logic."""

import asyncio
import json
from typing import Any

from google import genai
from google.genai import types
from google.genai.types import ThinkingLevel  # ADDED: Import ThinkingLevel
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import Config
from src.models import CopyRequest, CopyResponse, Platform
from src.prompt_builder import PromptBuilder
from src.validator import CopyValidator


class CopyGenerator:
    """Generates marketing copy via the Gemini API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        prompt_builder: PromptBuilder | None = None,
        validator: CopyValidator | None = None,
    ) -> None:
        """Initialize the copy generator."""

        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = model or Config.GEMINI_MODEL

        self.prompt_builder = prompt_builder or PromptBuilder()
        self.validator = validator or CopyValidator()

        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. " "Set GEMINI_API_KEY in .env"
            )

        self._client = genai.Client(api_key=self.api_key)

        logger.info(f"CopyGenerator initialized with Gemini model: {self.model}")

    def _generation_config(
        self,
        request: CopyRequest,
    ) -> types.GenerateContentConfig:
        """Build Gemini generation configuration."""

        response_schema = {
            "type": "OBJECT",
            "properties": {
                "platform": {
                    "type": "STRING",
                },
                "tone_used": {
                    "type": "STRING",
                },
                "temperature_used": {
                    "type": "NUMBER",
                },
                "top_p_used": {
                    "type": "NUMBER",
                },
                "character_count": {
                    "type": "INTEGER",
                },
                "copy": {
                    "type": "STRING",
                },
                "subject_line": {
                    "type": "STRING",
                    "nullable": True,
                },
                "hashtags": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING",
                    },
                },
                "validation_passed": {
                    "type": "BOOLEAN",
                },
                "validation_errors": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING",
                    },
                },
            },
            "required": [
                "platform",
                "tone_used",
                "temperature_used",
                "top_p_used",
                "character_count",
                "copy",
                "subject_line",
                "hashtags",
                "validation_passed",
                "validation_errors",
            ],
        }

        return types.GenerateContentConfig(
            system_instruction=(
                "You are a professional marketing copywriting engine. "
                "Return ONLY valid JSON matching the provided schema. "
                "Do not use markdown. "
                "Do not add explanations. "
                "Do not wrap the JSON in code fences."
            ),
            temperature=request.temperature,
            top_p=request.top_p,
            max_output_tokens=4096,
            response_mime_type="application/json",
            response_json_schema=response_schema,
            thinking_config=types.ThinkingConfig(
                thinking_level=ThinkingLevel.MINIMAL  # FIXED: Changed from "minimal" to ThinkingLevel.MINIMAL
            ),
        )

    @retry(
        stop=stop_after_attempt(Config.RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=1,
            max=60,
        ),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def generate_async(
        self,
        request: CopyRequest,
    ) -> CopyResponse:
        """Generate copy asynchronously with retry logic."""

        prompt = self.prompt_builder.build(request)

        logger.info(
            f"Generating async copy for '{request.product_name}' | "
            f"Platform: {request.platform.value} | "
            f"Tone: {request.tone.value}"
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self._generation_config(request),
            )

            # Debug Gemini response
            logger.debug(
                "GEMINI RESPONSE OBJECT: {}",
                response,
            )

            # Check candidate information
            if response.candidates:
                candidate = response.candidates[0]

                logger.debug(
                    "GEMINI FINISH REASON: {}",
                    candidate.finish_reason,
                )

                logger.debug(
                    "GEMINI FINISH MESSAGE: {}",
                    getattr(candidate, "finish_message", None),
                )

            finish_reason = None
            if response.candidates:
                finish_reason = response.candidates[0].finish_reason

            # A MAX_TOKENS response is commonly truncated JSON. Do not feed
            # partial JSON into json.loads(); fail clearly instead.
            if str(finish_reason).endswith("MAX_TOKENS"):
                raise RuntimeError(
                    "Gemini response was truncated by MAX_TOKENS. "
                    "The generator reserves additional output budget for Gemini 3.x thinking."
                )

            raw_content = response.text

            if not raw_content:
                raise ValueError("Empty response from Gemini API")

            logger.debug(
                "RAW GEMINI RESPONSE:\n{}",
                raw_content,
            )

            # Structured-output responses may already contain a parsed dict.
            # Prefer it and only fall back to JSON decoding for compatibility
            # with older SDK responses and tests.
            parsed = getattr(response, "parsed", None)
            if not isinstance(parsed, dict):
                try:
                    parsed = json.loads(raw_content)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Gemini JSON response: {e}")

                    logger.error(
                        "Raw Gemini response was:\n{}",
                        raw_content,
                    )

                    return self._create_error_response(
                        request,
                        f"JSON parse error: {str(e)}",
                    )

            # Convert Gemini response to our Pydantic model
            copy_response = self._parse_response(
                parsed,
                request,
            )

            # Validate generated copy
            copy_response = self.validator.validate(
                copy_response,
                request,
            )

            logger.info(
                f"Successfully generated copy "
                f"({copy_response.character_count} chars) "
                f"for '{request.product_name}'"
            )

            return copy_response

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def generate_sync(
        self,
        request: CopyRequest,
    ) -> CopyResponse:
        """Generate copy synchronously."""

        prompt = self.prompt_builder.build(request)

        logger.info(
            f"Generating sync copy for '{request.product_name}' | "
            f"Platform: {request.platform.value} | "
            f"Tone: {request.tone.value}"
        )

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self._generation_config(request),
            )

            finish_reason = None
            if response.candidates:
                finish_reason = response.candidates[0].finish_reason

            # A MAX_TOKENS response is commonly truncated JSON. Do not feed
            # partial JSON into json.loads(); fail clearly instead.
            if str(finish_reason).endswith("MAX_TOKENS"):
                raise RuntimeError(
                    "Gemini response was truncated by MAX_TOKENS. "
                    "The generator reserves additional output budget for Gemini 3.x thinking."
                )

            raw_content = response.text

            if not raw_content:
                raise ValueError("Empty response from Gemini API")

            logger.debug(
                "RAW GEMINI RESPONSE:\n{}",
                raw_content,
            )

            parsed = getattr(response, "parsed", None)
            if not isinstance(parsed, dict):
                try:
                    parsed = json.loads(raw_content)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Gemini JSON response: {e}")

                    logger.error(
                        "Raw Gemini response was:\n{}",
                        raw_content,
                    )

                    return self._create_error_response(
                        request,
                        f"JSON parse error: {str(e)}",
                    )

            copy_response = self._parse_response(
                parsed,
                request,
            )

            copy_response = self.validator.validate(
                copy_response,
                request,
            )

            logger.info(
                f"Successfully generated sync copy "
                f"({copy_response.character_count} chars)"
            )

            return copy_response

        except Exception as e:
            logger.error(f"Sync generation failed: {e}")

            return self._create_error_response(
                request,
                str(e),
            )

    async def generate_batch(
        self,
        requests: list[CopyRequest],
        max_concurrent: int | None = None,
    ) -> list[CopyResponse]:
        """Generate copy for multiple requests with concurrency control."""

        semaphore_limit = max_concurrent or Config.MAX_CONCURRENT_REQUESTS

        semaphore = asyncio.Semaphore(semaphore_limit)

        async def _bounded_generate(
            req: CopyRequest,
        ) -> CopyResponse:

            async with semaphore:

                try:
                    return await self.generate_async(req)

                except Exception as e:
                    logger.error(f"Batch item failed for " f"'{req.product_name}': {e}")

                    return self._create_error_response(
                        req,
                        str(e),
                    )

        logger.info(
            f"Starting batch generation for "
            f"{len(requests)} requests "
            f"(max_concurrent={semaphore_limit})"
        )

        tasks = [_bounded_generate(req) for req in requests]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        final_results: list[CopyResponse] = []

        for i, result in enumerate(results):

            if isinstance(result, Exception):

                logger.error(f"Request {i} raised exception: {result}")

                final_results.append(
                    self._create_error_response(
                        requests[i],
                        str(result),
                    )
                )

            elif isinstance(result, CopyResponse):  # ADDED: Type guard
                final_results.append(result)

            else:  # ADDED: Handle unexpected type
                final_results.append(
                    self._create_error_response(
                        requests[i],
                        f"Unexpected result type: {type(result)}",
                    )
                )

        success_count = sum(1 for r in final_results if r.validation_passed)

        logger.info(
            f"Batch complete: " f"{success_count}/{len(requests)} " f"passed validation"
        )

        return final_results

    def _parse_response(
        self,
        data: dict[str, Any],
        request: CopyRequest,
    ) -> CopyResponse:
        """Parse Gemini JSON response into CopyResponse."""

        copy_text = data.get(
            "copy",
            "",
        )

        if not isinstance(copy_text, str):
            copy_text = str(copy_text)

        char_count = data.get(
            "character_count",
            len(copy_text),
        )

        # Always use actual character count
        char_count = len(copy_text)

        # Platform
        platform_value = data.get(
            "platform",
            request.platform.value,
        )

        try:
            platform = Platform(platform_value)

        except ValueError:
            platform = request.platform

        # Subject line
        subject_line = None

        if request.platform == Platform.EMAIL:
            subject_line = data.get("subject_line")

        # Hashtags
        hashtags: list[str] = []

        if request.platform == Platform.INSTAGRAM:

            hashtags = data.get(
                "hashtags",
                [],
            )

            if not isinstance(hashtags, list):
                hashtags = []

        # Validation errors
        validation_errors = data.get(
            "validation_errors",
            [],
        )

        if not isinstance(validation_errors, list):
            validation_errors = []

        return CopyResponse(
            platform=platform,
            tone_used=request.tone,
            temperature_used=data.get(
                "temperature_used",
                request.temperature,
            ),
            top_p_used=data.get(
                "top_p_used",
                request.top_p,
            ),
            character_count=char_count,
            copy_text=copy_text,  # FIXED: Changed from 'copy=' to 'copy_text='
            subject_line=subject_line,
            hashtags=hashtags,
            validation_passed=data.get(
                "validation_passed",
                True,
            ),
            validation_errors=validation_errors,
            model_used=self.model,
        )

    def _create_error_response(
        self,
        request: CopyRequest,
        error_msg: str,
    ) -> CopyResponse:
        """Create a fallback error response."""

        logger.warning(
            f"Creating error response for " f"'{request.product_name}': {error_msg}"
        )

        fallback_copy = (
            f"We encountered an issue generating copy "
            f"for {request.product_name}. "
            f"Please try again with adjusted parameters. "
            f"Error: {error_msg}"
        )

        # Keep fallback within character limit
        if len(fallback_copy) > request.character_limit:

            fallback_copy = fallback_copy[: request.character_limit - 3] + "..."

        return CopyResponse(
            platform=request.platform,
            tone_used=request.tone,
            temperature_used=request.temperature,
            top_p_used=request.top_p,
            character_count=len(fallback_copy),
            copy_text=fallback_copy,  # FIXED: Changed from 'copy=' to 'copy_text='
            subject_line=(
                "Generation Error" if request.platform == Platform.EMAIL else None
            ),
            hashtags=(
                [
                    "#Error",
                    "#Retry",
                    "#TryAgain",
                ]
                if request.platform == Platform.INSTAGRAM
                else []
            ),
            validation_passed=False,
            validation_errors=[error_msg],
            model_used=self.model,
        )
