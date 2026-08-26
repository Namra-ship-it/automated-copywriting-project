"""Tests for prompt template engine."""

import pytest

from src.models import CopyRequest, Platform, Tone
from src.prompt_builder import PromptBuilder


class TestPromptBuilder:
    """Test suite for PromptBuilder."""
    @pytest.fixture
    def builder(self):
        return PromptBuilder()

    @pytest.fixture
    def sample_request(self):
        return CopyRequest(
            product_name="EcoCharge Pro",
            product_description="Portable solar power bank with 20000mAh capacity.",
            platform=Platform.INSTAGRAM,
            tone=Tone.ECO_CONSCIOUS,
            target_audience="Outdoor enthusiasts",
            character_limit=2200,
            call_to_action="Shop now",
            temperature=0.8,
            top_p=0.9,
        )

    def test_template_loading(self, builder):
        assert len(builder._template) > 0
        assert "{product_name}" in builder._template

    def test_platform_instructions_loading(self, builder):
        assert "LinkedIn" in builder._instructions
        assert "Instagram" in builder._instructions

    def test_prompt_building(self, builder, sample_request):
        prompt = builder.build(sample_request)
        assert "EcoCharge Pro" in prompt
        assert "Instagram" in prompt
        assert "Eco-conscious" in prompt
        assert "Shop now" in prompt

    def test_sanitization(self, builder, sample_request):
        sample_request.product_name = "  Product   Name  "
        prompt = builder.build(sample_request)
        assert "  Product   Name  " not in prompt
        assert "Product Name" in prompt

    def test_temperature_instructions(self, builder):
        low = builder._get_temperature_instructions(0.3)
        assert "conservative" in low.lower()
        med = builder._get_temperature_instructions(0.8)
        assert "balanced" in med.lower()
        high = builder._get_temperature_instructions(1.5)
        assert "creative" in high.lower()
