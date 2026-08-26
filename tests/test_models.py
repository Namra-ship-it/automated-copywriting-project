"""Pytest tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from src.models import CopyRequest, CopyResponse, Platform, Tone


class TestCopyRequest:
    """Tests for CopyRequest validation."""

    def test_valid_request(self):
        req = CopyRequest(
            product_name="Test Product",
            product_description="A comprehensive test product description.",
            platform=Platform.LINKEDIN,
            tone=Tone.PROFESSIONAL,
            target_audience="B2B executives",
            character_limit=3000,
            call_to_action="Learn more",
            temperature=0.7,
            top_p=0.9,
        )
        assert req.product_name == "Test Product"
        assert req.platform == Platform.LINKEDIN

    def test_temperature_out_of_range(self):
        with pytest.raises(ValidationError) as exc_info:
            CopyRequest(
                product_name="Test",
                product_description="Valid description here.",
                platform=Platform.INSTAGRAM,
                tone=Tone.CASUAL,
                target_audience="Gen Z",
                call_to_action="Buy now",
                temperature=2.5,
            )
        assert "temperature" in str(exc_info.value).lower()

    def test_top_p_out_of_range(self):
        with pytest.raises(ValidationError) as exc_info:
            CopyRequest(
                product_name="Test",
                product_description="Valid description here.",
                platform=Platform.EMAIL,
                tone=Tone.PERSUASIVE,
                target_audience="Everyone",
                call_to_action="Sign up",
                top_p=1.5,
            )
        assert "top_p" in str(exc_info.value).lower()

    def test_description_too_short(self):
        with pytest.raises(ValidationError) as exc_info:
            CopyRequest(
                product_name="Test",
                product_description="Short",
                platform=Platform.LINKEDIN,
                tone=Tone.PROFESSIONAL,
                target_audience="CEOs",
                call_to_action="Click here",
            )
        assert "description" in str(exc_info.value).lower()

    def test_whitespace_stripping(self):
        req = CopyRequest(
            product_name="  Trimmed Product  ",
            product_description="A valid product description that is long enough.",
            platform=Platform.INSTAGRAM,
            tone=Tone.HUMOROUS,
            target_audience="Millennials",
            call_to_action="Shop now",
        )
        assert req.product_name == "Trimmed Product"


class TestCopyResponse:
    """Tests for CopyResponse validation."""

    def test_valid_response(self):
        resp = CopyResponse(
            platform=Platform.LINKEDIN,
            tone_used=Tone.PROFESSIONAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=33,
            copy_text="This is a test copy for LinkedIn.",
            validation_passed=True,
            validation_errors=[],
        )
        assert resp.validation_passed is True

    def test_email_requires_subject_line(self):
        resp = CopyResponse(
            platform=Platform.EMAIL,
            tone_used=Tone.PROFESSIONAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=200,
            copy_text="Email body content here.",
        )
        assert resp.validation_passed is False

    def test_instagram_requires_hashtags(self):
        resp = CopyResponse(
            platform=Platform.INSTAGRAM,
            tone_used=Tone.CASUAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=100,
            copy_text="Instagram post content.",
        )
        assert resp.validation_passed is False

    def test_character_count_mismatch(self):
        resp = CopyResponse(
            platform=Platform.LINKEDIN,
            tone_used=Tone.PROFESSIONAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=150,
            copy_text="Short copy.",
        )
        assert resp.validation_passed is False
        assert any("mismatch" in err for err in resp.validation_errors)


class TestEnums:
    """Tests for Platform and Tone enums."""

    def test_platform_values(self):
        assert Platform.LINKEDIN.value == "LinkedIn"
        assert Platform.INSTAGRAM.value == "Instagram"
        assert Platform.EMAIL.value == "Email"

    def test_tone_values(self):
        assert Tone.PROFESSIONAL.value == "Professional"
        assert Tone.ECO_CONSCIOUS.value == "Eco-conscious"
        assert Tone.ADVENTUROUS.value == "Adventurous"
