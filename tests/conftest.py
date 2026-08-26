"""Pytest fixtures for the copywriting engine tests."""

import pytest

from src.generator import CopyGenerator
from src.models import CopyRequest, Platform, Tone
from src.validator import CopyValidator


@pytest.fixture
def generator():
    """Create a CopyGenerator instance for testing."""
    return CopyGenerator()


@pytest.fixture
def validator():
    """Create a CopyValidator instance for testing."""
    return CopyValidator()


@pytest.fixture
def sample_request():
    """Create a sample CopyRequest for testing."""
    return CopyRequest(
        product_name="Test Product",
        product_description="A great product for testing.",
        platform=Platform.LINKEDIN,
        tone=Tone.PROFESSIONAL,
        target_audience="Testers",
        character_limit=3000,
        call_to_action="Learn more",
        temperature=0.7,
        top_p=0.9,
        max_tokens=500,
    )


@pytest.fixture
def base_request():
    """Create a base CopyRequest for validation tests."""
    return CopyRequest(
        product_name="Test Product",
        product_description="A product for testing validation.",
        platform=Platform.INSTAGRAM,
        tone=Tone.CASUAL,
        target_audience="Testers",
        character_limit=2200,
        call_to_action="Buy now",
        temperature=0.7,
        top_p=0.9,
        max_tokens=500,
    )
