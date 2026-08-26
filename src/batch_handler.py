"""Batch processing orchestrator for high-volume copy generation."""

import asyncio
from pathlib import Path

from loguru import logger

from src.async_handler import AsyncHandler
from src.config import Config
from src.generator import CopyGenerator
from src.models import CopyRequest, CopyResponse
from src.utils import read_json_file, write_json_file


class BatchHandler:
    """Handles batch processing of copy generation requests.

    Loads inputs from JSON files, processes them concurrently via
    AsyncHandler, and saves results to structured output files.
    """

    def __init__(
        self,
        generator: CopyGenerator | None = None,
        async_handler: AsyncHandler | None = None,
        output_dir: Path | None = None,
    ) -> None:
        """Initialize the batch handler.

        Args:
            generator: CopyGenerator instance. Creates default if None.
            async_handler: AsyncHandler instance. Creates default if None.
            output_dir: Directory for batch output files.
        """
        self.generator = generator or CopyGenerator()
        self.async_handler = async_handler or AsyncHandler()
        self.output_dir = output_dir or Config.OUTPUTS_DIR / "batch"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"BatchHandler initialized with output_dir={self.output_dir}")

    def run_batch(self, requests: list[CopyRequest]) -> list[CopyResponse]:
        """Run batch processing synchronously (wraps async execution).

        Args:
            requests: List of copy generation requests.

        Returns:
            List of copy responses.
        """
        logger.info(f"Running batch for {len(requests)} requests")
        return asyncio.run(self._run_batch_async(requests))

    async def _run_batch_async(self, requests: list[CopyRequest]) -> list[CopyResponse]:
        """Async implementation of batch processing.

        Args:
            requests: List of copy generation requests.

        Returns:
            List of copy responses.
        """

        # FIXED: Create coroutines WITHOUT any parameters
        # We use a closure with default argument to capture req by value
        def make_coroutine(req: CopyRequest):
            async def coroutine():
                return await self.generator.generate_async(req)

            return coroutine

        coros = [make_coroutine(req) for req in requests]

        request_ids = [f"{req.product_name}_{i}" for i, req in enumerate(requests)]

        results = await self.async_handler.process_batch(coros, request_ids)

        # Handle results properly
        responses: list[CopyResponse] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch item {i} failed: {result}")
                responses.append(
                    self.generator._create_error_response(requests[i], str(result))
                )
            elif isinstance(result, CopyResponse):
                responses.append(result)
            else:
                # Handle unexpected type (shouldn't happen, but just in case)
                logger.error(f"Batch item {i} returned unexpected type: {type(result)}")
                responses.append(
                    self.generator._create_error_response(
                        requests[i], f"Unexpected result type: {type(result)}"
                    )
                )

        return responses

    def save_batch_results(
        self,
        responses: list[CopyResponse],
        output_file: Path | str | None = None,
    ) -> Path:
        """Save batch results to a JSON file.

        Args:
            responses: List of copy responses to save.
            output_file: Output file path. Auto-generated if None.

        Returns:
            Path to the saved output file.
        """
        if output_file is None:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"batch_results_{timestamp}.json"
        else:
            output_file = Path(output_file)

        data = {
            "meta": {
                "total_requests": len(responses),
                "successful": sum(1 for r in responses if r.validation_passed),
                "failed": sum(1 for r in responses if not r.validation_passed),
            },
            "results": [r.to_dict() for r in responses],
        }

        write_json_file(output_file, data)
        logger.info(f"Batch results saved to {output_file}")
        return output_file

    def load_batch_inputs(self, input_file: Path | str) -> list[CopyRequest]:
        """Load batch input requests from a JSON file.

        Expected JSON format:
        {
          "requests": [
            {
              "product_name": "...",
              "product_description": "...",
              ...
            }
          ]
        }

        Args:
            input_file: Path to JSON file containing requests.

        Returns:
            List of validated CopyRequest objects.
        """
        path = Path(input_file)
        data = read_json_file(path)

        if isinstance(data, list):
            raw_requests = data
        elif isinstance(data, dict) and "requests" in data:
            raw_requests = data["requests"]
        else:
            raise ValueError(
                "Invalid batch input format. Expected list or dict with 'requests' key."
            )

        requests: list[CopyRequest] = []
        for i, raw in enumerate(raw_requests):
            try:
                req = CopyRequest(**raw)
                requests.append(req)
            except Exception as e:
                logger.error(f"Failed to validate request {i}: {e}")
                raise

        logger.info(f"Loaded {len(requests)} batch requests from {path}")
        return requests

    def process_file(
        self,
        input_file: Path | str,
        output_file: Path | str | None = None,
    ) -> Path:
        """End-to-end batch processing from file input to file output.

        Args:
            input_file: Path to JSON input file.
            output_file: Path for JSON output file. Auto-generated if None.

        Returns:
            Path to the saved output file.
        """
        requests = self.load_batch_inputs(input_file)
        responses = self.run_batch(requests)
        return self.save_batch_results(responses, output_file)
