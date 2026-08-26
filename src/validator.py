"""Output validation and brand safety enforcement."""

import re

from loguru import logger

from src.models import CopyRequest, CopyResponse, Platform


class CopyValidator:
    """Validates generated copy against platform rules and brand safety guidelines."""

    def __init__(self) -> None:
        """Initialize the validator."""
        self.platform_limits = {
            Platform.LINKEDIN: 3000,
            Platform.INSTAGRAM: 2200,
            Platform.EMAIL: 5000,
        }

    def validate(
        self,
        response: CopyResponse,
        request: CopyRequest,
    ) -> CopyResponse:
        """Validate a copy response against request constraints."""

        errors: list[str] = []

        # Character limit enforcement. Never allow a request to exceed the
        # platform's own hard limit.
        platform_limit = self.platform_limits.get(
            response.platform, request.character_limit
        )
        effective_limit = min(request.character_limit, platform_limit)

        if response.character_count > effective_limit:
            errors.append(
                f"Character limit exceeded: "
                f"{response.character_count} > {effective_limit}"
            )

            # FIXED: Changed response.copy to response.copy_text
            response.copy_text = response.copy_text[:effective_limit]
            response.character_count = len(response.copy_text)  # FIXED

        # Platform-specific validation
        if response.platform == Platform.EMAIL:
            if not response.subject_line:
                errors.append("Email platform requires a non-null subject_line.")
                response.subject_line = f"Introducing {request.product_name}"

        if response.platform == Platform.INSTAGRAM:
            if not (3 <= len(response.hashtags) <= 5):
                errors.append(
                    f"Instagram requires 3-5 hashtags, "
                    f"got {len(response.hashtags)}."
                )

                if len(response.hashtags) < 3:
                    defaults = [
                        f"#{request.product_name.replace(' ', '')}",
                        "#MustHave",
                        "#NewLaunch",
                    ]

                    response.hashtags = (response.hashtags + defaults)[:5]

        # Verify character count - FIXED: Changed response.copy to response.copy_text
        actual_count = len(response.copy_text)

        if response.character_count != actual_count:
            response.character_count = actual_count

        # Brand safety check
        exaggerated_words = [
            "best",
            "perfect",
            "unbeatable",
            "revolutionary",
            "guaranteed",
        ]

        # FIXED: Changed response.copy to response.copy_text
        copy_lower = response.copy_text.lower()

        for word in exaggerated_words:
            # Match complete words only; e.g. do not flag "best" inside
            # another word. "Best regards" is an email sign-off, not a claim.
            if not re.search(rf"\b{re.escape(word)}\b", copy_lower):
                continue

            if word == "best" and re.search(r"\bbest\s+regards\b", copy_lower):
                continue

            errors.append(f"Potential exaggerated claim detected: '{word}'")

        # Final validation result
        if errors:
            response.validation_passed = False
            response.validation_errors = errors

            logger.warning(f"Validation failed with {len(errors)} errors: {errors}")
        else:
            response.validation_passed = True
            response.validation_errors = []

        return response

    def validate_character_limit(
        self,
        text: str,
        limit: int,
    ) -> tuple[bool, int]:
        """Check if text is within character limit."""

        count = len(text)

        return count <= limit, count
