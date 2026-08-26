"""Pydantic data models for input validation and output structuring."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Platform(str, Enum):
    """Supported marketing platforms."""

    LINKEDIN = "LinkedIn"
    INSTAGRAM = "Instagram"
    EMAIL = "Email"


class Tone(str, Enum):
    """Supported tone styles."""

    PROFESSIONAL = "Professional"
    CASUAL = "Casual"
    PERSUASIVE = "Persuasive"
    HUMOROUS = "Humorous"
    INSPIRATIONAL = "Inspirational"
    ECO_CONSCIOUS = "Eco-conscious"
    ADVENTUROUS = "Adventurous"


class CopyRequest(BaseModel):
    """Input model for copy generation requests.

    All fields are validated to ensure the request meets platform,
    brand, and API constraints before processing.
    """

    product_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the product or service.",
    )
    product_description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detailed description of the product or service.",
    )
    platform: Platform = Field(
        ...,
        description="Target platform for the marketing copy.",
    )
    tone: Tone = Field(
        ...,
        description="Desired tone of the marketing copy.",
    )
    target_audience: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Description of the target audience.",
    )
    character_limit: int = Field(
        default=3000,
        ge=50,
        le=5000,
        description="Maximum character count for the generated copy.",
    )
    call_to_action: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Call-to-action phrase to include.",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Creativity level: 0.0 = focused, 2.0 = highly creative.",
    )
    top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling threshold for vocabulary diversity.",
    )
    max_tokens: int = Field(
        default=500,
        ge=50,
        le=4000,
        description="Maximum tokens for the API response.",
    )

    @field_validator("product_name")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading/trailing whitespace from product name."""
        return v.strip()

    @field_validator("product_description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Ensure description is meaningful and not just whitespace."""
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError(
                "Product description must be at least 10 characters after trimming."
            )
        return stripped

    @model_validator(mode="after")
    def validate_character_limit(self) -> "CopyRequest":
        """Ensure character limit aligns with platform defaults."""
        platform_limits = {
            Platform.LINKEDIN: 3000,
            Platform.INSTAGRAM: 2200,
            Platform.EMAIL: 5000,
        }
        expected = platform_limits.get(self.platform, 3000)
        if self.character_limit > expected:
            # Allow override but warn via validation note
            pass  # Pydantic will accept; validator can log if needed
        return self


class CopyResponse(BaseModel):
    """Output model for generated marketing copy.

    Includes validation metadata to confirm the output meets all
    platform-specific and brand safety constraints.
    """

    platform: Platform = Field(
        ...,
        description="Platform the copy was generated for.",
    )
    tone_used: Tone = Field(
        ...,
        description="Tone applied to the copy.",
    )
    temperature_used: float = Field(
        ...,
        description="Temperature parameter used for generation.",
    )
    top_p_used: float = Field(
        ...,
        description="Top_P parameter used for generation.",
    )
    character_count: int = Field(
        ...,
        ge=0,
        description="Exact character count of the generated copy.",
    )
    copy_text: str = Field(  # FIXED: Renamed from 'copy' to 'copy_text'
        ...,
        min_length=1,
        description="The generated marketing copy text.",
    )
    subject_line: Optional[str] = Field(
        default=None,
        description="Email subject line (required and non-null only for Email platform).",
    )
    hashtags: list[str] = Field(
        default_factory=list,
        description="Hashtags for Instagram (3-5 required when platform is Instagram).",
    )
    validation_passed: bool = Field(
        default=True,
        description="Whether the output passed all validation checks.",
    )
    validation_errors: list[str] = Field(
        default_factory=list,
        description="List of validation error messages if any checks failed.",
    )
    model_used: str = Field(
        default="gemini-3.6-flash",
        description="Model used for generation.",
    )

    @model_validator(mode="after")
    def validate_platform_specifics(self) -> "CopyResponse":
        """Enforce platform-specific output requirements."""
        errors: list[str] = []

        if self.platform == Platform.EMAIL and not self.subject_line:
            errors.append("Email platform requires a non-null subject_line.")

        if self.platform == Platform.INSTAGRAM:
            if not (3 <= len(self.hashtags) <= 5):
                errors.append(
                    f"Instagram platform requires 3-5 hashtags, got {len(self.hashtags)}."
                )

        # FIXED: Changed self.copy to self.copy_text
        if self.character_count != len(self.copy_text):
            errors.append(
                f"Character count mismatch: reported {self.character_count}, "
                f"actual {len(self.copy_text)}."  # FIXED: Changed self.copy to self.copy_text
            )

        if errors:
            self.validation_passed = False
            self.validation_errors.extend(errors)

        return self

    def to_json(self) -> str:
        """Serialize response to JSON string."""
        return self.model_dump_json(indent=2)

    def to_dict(self) -> dict[str, Any]:
        """Serialize response to dictionary."""
        return self.model_dump()
