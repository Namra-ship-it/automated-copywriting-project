"""Tests for the Gemini API generator."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models import CopyResponse, Platform


class TestCopyGenerator:
    """Test suite for CopyGenerator."""

    def test_init(self, generator):
        """Test generator initialization."""
        assert generator.model == "gemini-3.6-flash"
        assert generator.api_key is not None
        assert generator.prompt_builder is not None
        assert generator.validator is not None

    def test_parse_response(self, generator, sample_request):
        """Test parsing Gemini JSON response."""
        raw = {
            "platform": "LinkedIn",
            "copy": "This is generated copy.",
            "character_count": 23,
            "subject_line": None,
            "hashtags": [],
            "validation_passed": True,
            "validation_errors": [],
        }

        response = generator._parse_response(raw, sample_request)

        # FIXED: Changed response.copy to response.copy_text
        assert response.copy_text == "This is generated copy."
        assert response.character_count == 23
        assert response.platform == Platform.LINKEDIN

    def test_error_response_creation(self, generator, sample_request):
        """Test error response creation."""
        error_resp = generator._create_error_response(sample_request, "API failure")

        assert error_resp.validation_passed is False
        assert "API failure" in error_resp.validation_errors[0]
        # FIXED: Changed error_resp.copy to error_resp.copy_text
        assert sample_request.product_name in error_resp.copy_text

    @pytest.mark.asyncio
    async def test_generate_async_success(self, generator, sample_request):
        """Test successful async generation."""
        mock_response = MagicMock()

        mock_response.text = json.dumps(
            {
                "platform": "LinkedIn",
                "copy": "Generated LinkedIn copy.",
                "character_count": 25,
                "subject_line": None,
                "hashtags": [],
                "validation_passed": True,
                "validation_errors": [],
            }
        )

        generator._client.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )

        result = await generator.generate_async(sample_request)

        assert isinstance(result, CopyResponse)
        # FIXED: Changed result.copy to result.copy_text
        assert result.copy_text == "Generated LinkedIn copy."
        assert result.character_count == 24  # Actual character count

    @pytest.mark.asyncio
    async def test_generate_async_json_error(self, generator, sample_request):
        """Test async generation with JSON parse error."""
        mock_response = MagicMock()

        mock_response.text = "invalid json"

        generator._client.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )

        result = await generator.generate_async(sample_request)

        assert isinstance(result, CopyResponse)
        assert result.validation_passed is False
        assert "JSON parse error" in result.validation_errors[0]

    def test_generation_config(self, generator, sample_request):
        """Test generation config creation."""
        config = generator._generation_config(sample_request)

        assert config.temperature == sample_request.temperature
        assert config.top_p == sample_request.top_p
        assert config.response_mime_type == "application/json"
        assert "marketing copywriting engine" in config.system_instruction
