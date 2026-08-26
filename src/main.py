"""Main entry points and orchestration for the copywriting engine."""

import asyncio
from pathlib import Path

from loguru import logger

from src.batch_handler import BatchHandler
from src.config import Config
from src.generator import CopyGenerator
from src.models import CopyRequest, CopyResponse, Platform, Tone
from src.utils import setup_file_logger


def setup_logging(
    log_dir: Path | None = None,
    level: str | None = None,
) -> None:
    """Configure application logging.

    Args:
        log_dir: Directory for log files.
        level: Logging level.
    """
    log_dir = log_dir or Config.LOGS_DIR
    level = level or Config.LOG_LEVEL

    setup_file_logger(log_dir, level)

    logger.info("Logging configured successfully")


async def run_real_time(
    request: CopyRequest,
) -> CopyResponse:
    """Process a single real-time copy generation request.

    Args:
        request: Copy generation request.

    Returns:
        CopyResponse with generated copy.
    """
    logger.info(f"Running real-time generation for " f"'{request.product_name}'")

    generator = CopyGenerator()

    return await generator.generate_async(request)


def run_batch(
    requests: list[CopyRequest],
) -> list[CopyResponse]:
    """Process multiple requests in batch mode.

    Args:
        requests: List of copy generation requests.

    Returns:
        List of copy responses.
    """
    logger.info(f"Running batch generation for " f"{len(requests)} requests")

    handler = BatchHandler()

    return handler.run_batch(requests)


def run_batch_from_file(
    input_file: Path | str,
    output_file: Path | str | None = None,
) -> Path:
    """Process batch requests from a JSON file.

    Args:
        input_file: Path to JSON input file.
        output_file: Path for JSON output file.

    Returns:
        Path to saved output file.
    """
    logger.info(f"Running batch from file: {input_file}")

    handler = BatchHandler()

    return handler.process_file(
        input_file,
        output_file,
    )


def main() -> None:
    """Example main function demonstrating usage."""

    setup_logging()

    # Example real-time request
    request = CopyRequest(
        product_name="EcoCharge Pro",
        product_description=(
            "A portable solar power bank with "
            "20000mAh capacity, waterproof, and "
            "built-in LED flashlight"
        ),
        platform=Platform.INSTAGRAM,
        tone=Tone.ECO_CONSCIOUS,
        target_audience=("Outdoor enthusiasts and eco-friendly travelers"),
        character_limit=2200,
        call_to_action="Shop now and go green",
        temperature=0.8,
        top_p=0.9,
        max_tokens=2048,
    )

    logger.info(f"Request configured with " f"max_tokens={request.max_tokens}")

    response = asyncio.run(run_real_time(request))

    print(response.to_json())


if __name__ == "__main__":
    main()
