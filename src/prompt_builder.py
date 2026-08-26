"""Prompt template engine with dynamic compilation and sanitization."""

import json
from pathlib import Path
from typing import Any

from loguru import logger

from src.config import Config
from src.models import CopyRequest
from src.utils import sanitize_text


class PromptBuilder:
    """Builds and compiles prompts from templates with variable injection.

    Loads master template, platform instructions, and brand guidelines,
    then interpolates request variables to produce a final prompt string.
    """

    def __init__(
        self,
        template_path: Path | None = None,
        instructions_path: Path | None = None,
        guidelines_path: Path | None = None,
    ) -> None:
        """Initialize the prompt builder with template files.

        Args:
            template_path: Path to master_template.txt. Defaults to prompts/master_template.txt.
            instructions_path: Path to platform_instructions.json. Defaults to prompts/platform_instructions.json.
            guidelines_path: Path to brand_guidelines.txt. Defaults to prompts/brand_guidelines.txt.
        """
        self.template_path = template_path or Config.PROMPTS_DIR / "master_template.txt"
        self.instructions_path = (
            instructions_path or Config.PROMPTS_DIR / "platform_instructions.json"
        )
        self.guidelines_path = (
            guidelines_path or Config.PROMPTS_DIR / "brand_guidelines.txt"
        )

        self._template: str = ""
        self._instructions: dict[str, Any] = {}
        self._guidelines: str = ""

        self._load_resources()

    def _load_resources(self) -> None:
        """Load template, instructions, and guidelines from disk."""
        try:
            with self.template_path.open("r", encoding="utf-8") as f:
                self._template = f.read()
            logger.debug(f"Loaded master template from {self.template_path}")
        except FileNotFoundError:
            logger.error(f"Master template not found at {self.template_path}")
            raise

        try:
            with self.instructions_path.open("r", encoding="utf-8") as f:
                self._instructions = json.load(f)
            logger.debug(f"Loaded platform instructions from {self.instructions_path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load platform instructions: {e}")
            raise

        try:
            with self.guidelines_path.open("r", encoding="utf-8") as f:
                self._guidelines = f.read()
            logger.debug(f"Loaded brand guidelines from {self.guidelines_path}")
        except FileNotFoundError:
            logger.error(f"Brand guidelines not found at {self.guidelines_path}")
            raise

    def _format_platform_instructions(self, platform: str) -> str:
        """Format platform-specific instructions as a readable string.

        Args:
            platform: Platform name (LinkedIn, Instagram, Email).

        Returns:
            Formatted instructions string.
        """
        data = self._instructions.get(platform, {})
        if not data:
            logger.warning(f"No instructions found for platform: {platform}")
            return f"No specific instructions available for {platform}."

        lines = [
            f"Platform: {platform}",
            f"Format: {data.get('format', 'N/A')}",
            f"Style: {data.get('style', 'N/A')}",
            f"Character Limit: {data.get('char_limit', 'N/A')}",
            "Guidelines:",
        ]
        for guideline in data.get("guidelines", []):
            lines.append(f"  - {guideline}")

        return "\n".join(lines)

    def build(self, request: CopyRequest) -> str:
        """Compile the final prompt from template and request variables.

        Sanitizes all text inputs to prevent prompt injection and ensure
        JSON compatibility in the model response.

        Args:
            request: Validated copy generation request.

        Returns:
            Compiled prompt string ready for the DeepSeek API.
        """
        platform_instructions = self._format_platform_instructions(
            request.platform.value
        )

        # Apply temperature-specific instructions
        temp_instructions = self._get_temperature_instructions(request.temperature)

        prompt = self._template.format(
            product_name=sanitize_text(request.product_name),
            product_description=sanitize_text(request.product_description),
            platform=request.platform.value,
            tone=request.tone.value,
            audience=sanitize_text(request.target_audience),
            char_limit=request.character_limit,
            cta=sanitize_text(request.call_to_action),
            temperature=request.temperature,
            top_p=request.top_p,
            platform_instructions=platform_instructions,
            brand_guidelines=self._guidelines,
            temperature_instructions=temp_instructions,
        )

        # Final sanitization pass
        prompt = sanitize_text(prompt)

        logger.info(
            f"Built prompt for product '{request.product_name}' on {request.platform.value}"
        )
        return prompt

    def _get_temperature_instructions(self, temperature: float) -> str:
        """Generate temperature-specific guidance.

        Args:
            temperature: The temperature value.

        Returns:
            Instruction string for the model.
        """
        if temperature < 0.5:
            return (
                "Temperature is set to conservative mode (< 0.5). "
                "Generate highly predictable, focused copy with minimal creative variation. "
                "Stick to proven messaging patterns."
            )
        elif temperature <= 1.2:
            return (
                "Temperature is set to balanced mode (0.5 - 1.2). "
                "Use controlled creativity while maintaining brand consistency. "
                "Explore fresh angles without risking off-brand messaging."
            )
        else:
            return (
                "Temperature is set to high-creative mode (> 1.2). "
                "Generate highly creative, potentially surprising outputs. "
                "Push creative boundaries while strictly maintaining brand safety guidelines."
            )

    def reload(self) -> None:
        """Reload template resources from disk. Useful for hot-reloading in development."""
        logger.info("Reloading prompt templates from disk...")
        self._load_resources()
