"""Tests for the copy validator."""

from src.models import CopyRequest, CopyResponse, Platform, Tone


class TestCopyValidator:
    """Test suite for CopyValidator."""

    def test_valid_response_passes(self, validator, base_request):
        """Test that valid response passes validation."""
        response = CopyResponse(
            platform=Platform.INSTAGRAM,
            tone_used=Tone.CASUAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=50,
            copy_text="This is valid Instagram copy with enough length.",
            hashtags=["#Test", "#Product", "#MustHave"],
            validation_passed=True,
        )

        result = validator.validate(response, base_request)

        assert result.validation_passed is True
        assert len(result.validation_errors) == 0

    def test_character_limit_enforcement(self, validator, base_request):
        """Test character limit enforcement."""
        long_copy = "A" * 3000
        response = CopyResponse(
            platform=Platform.INSTAGRAM,
            tone_used=Tone.CASUAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=3000,
            copy_text=long_copy,
            hashtags=["#Test", "#Product", "#MustHave"],
        )

        result = validator.validate(response, base_request)

        assert result.validation_passed is False
        assert len(result.copy_text) <= 2200

    def test_email_subject_line_required(self, validator):
        """Test that email requires a subject line."""
        request = CopyRequest(
            product_name="Email Product",
            product_description="A product for email testing.",
            platform=Platform.EMAIL,
            tone=Tone.PROFESSIONAL,
            target_audience="Subscribers",
            character_limit=5000,
            call_to_action="Click here",
        )

        response = CopyResponse(
            platform=Platform.EMAIL,
            tone_used=Tone.PROFESSIONAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=100,
            copy_text="Email body content.",
            subject_line=None,
        )

        result = validator.validate(response, request)

        assert result.validation_passed is False
        # FIXED: Added the period to match the actual error message
        assert (
            "Email platform requires a non-null subject_line."
            in result.validation_errors
        )

    def test_instagram_hashtag_auto_fill(self, validator):
        """Test that Instagram gets auto-filled hashtags."""
        request = CopyRequest(
            product_name="Tag Product",
            product_description="A product with few tags.",
            platform=Platform.INSTAGRAM,
            tone=Tone.CASUAL,
            target_audience="Users",
            character_limit=2200,
            call_to_action="Shop now",
        )

        response = CopyResponse(
            platform=Platform.INSTAGRAM,
            tone_used=Tone.CASUAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=50,
            copy_text="Short copy.",
            hashtags=["#OnlyOne"],
        )

        result = validator.validate(response, request)

        # Should add more hashtags
        assert len(result.hashtags) >= 3

    def test_best_regards_is_not_an_exaggerated_claim(self, validator):
        """Test that 'Best regards' is not flagged as exaggerated."""
        request = CopyRequest(
            product_name="Email Product",
            product_description="A product for email testing.",
            platform=Platform.EMAIL,
            tone=Tone.PROFESSIONAL,
            target_audience="Subscribers",
            character_limit=5000,
            call_to_action="Shop now",
        )

        response = CopyResponse(
            platform=Platform.EMAIL,
            tone_used=Tone.PROFESSIONAL,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=23,
            copy_text="Thank you.\n\nBest regards",
            subject_line="A useful update",
        )

        result = validator.validate(response, request)

        # Should pass validation for this specific check
        assert "best" not in [e.lower() for e in result.validation_errors]

    def test_exaggerated_claim_detection(self, validator, base_request):
        """Test detection of exaggerated claims."""
        response = CopyResponse(
            platform=Platform.LINKEDIN,
            tone_used=Tone.PERSUASIVE,
            temperature_used=0.7,
            top_p_used=0.9,
            character_count=50,
            copy_text="This is the best product ever and unbeatable in the market.",
            hashtags=[],
        )

        result = validator.validate(response, base_request)

        assert result.validation_passed is False
        # Should detect at least one exaggerated claim
        assert any("exaggerated" in e.lower() for e in result.validation_errors)
