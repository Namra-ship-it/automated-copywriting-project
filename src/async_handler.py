"""Async concurrency control with exponential backoff and jitter."""

import asyncio
import random
from typing import Any, Callable, Coroutine, TypeVar

from loguru import logger

from src.config import Config

T = TypeVar("T")


class AsyncHandler:
    """Manages asynchronous request processing with concurrency limits,
    exponential backoff, and jitter for resilient API interactions.
    """

    def __init__(
        self,
        max_concurrent: int | None = None,
        retry_attempts: int | None = None,
        backoff_multiplier: float | None = None,
        jitter_range: float | None = None,
    ) -> None:
        """Initialize the async handler.

        Args:
            max_concurrent: Semaphore limit for concurrent requests.
            retry_attempts: Maximum retry attempts per request.
            backoff_multiplier: Base multiplier for exponential backoff.
            jitter_range: Random jitter range (±value).
        """
        self.max_concurrent = max_concurrent or Config.MAX_CONCURRENT_REQUESTS
        self.retry_attempts = retry_attempts or Config.RETRY_ATTEMPTS
        self.backoff_multiplier = backoff_multiplier or Config.BACKOFF_MULTIPLIER
        self.jitter_range = jitter_range or Config.JITTER_RANGE

        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        logger.info(
            f"AsyncHandler initialized: max_concurrent={self.max_concurrent}, "
            f"retries={self.retry_attempts}, backoff={self.backoff_multiplier}, "
            f"jitter=±{self.jitter_range}"
        )

    async def process_request_with_retry(
        self,
        coro: Callable[[], Coroutine[Any, Any, T]],
        request_id: str = "",
    ) -> T:
        """Execute a coroutine with retry logic and exponential backoff.

        The delay formula is: delay = multiplier * (2 ** attempt) ± jitter

        Args:
            coro: Coroutine factory (call with no args to create fresh coroutine).
            request_id: Identifier for logging purposes.

        Returns:
            Result of the coroutine.

        Raises:
            Exception: If all retry attempts are exhausted.
        """
        last_exception: Exception | None = None

        for attempt in range(self.retry_attempts + 1):
            try:
                async with self._semaphore:
                    logger.debug(
                        f"[{request_id}] Attempt {attempt + 1}/{self.retry_attempts + 1}"
                    )
                    return await coro()
            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts:
                    # Calculate exponential backoff with jitter
                    base_delay = self.backoff_multiplier * (2**attempt)
                    jitter = random.uniform(-self.jitter_range, self.jitter_range)
                    delay = base_delay + jitter
                    delay = max(0.1, delay)  # Ensure non-negative minimum

                    logger.warning(
                        f"[{request_id}] Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"[{request_id}] All {self.retry_attempts + 1} attempts failed. "
                        f"Last error: {e}"
                    )

        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected state: no exception but all attempts failed")

    async def process_batch(
        self,
        coros: list[Callable[[], Coroutine[Any, Any, T]]],
        request_ids: list[str] | None = None,
    ) -> list[T | BaseException]:  # FIXED: Changed Exception to BaseException
        """Process multiple coroutines with controlled concurrency.

        Uses asyncio.gather with return_exceptions=True for error isolation.

        Args:
            coros: List of coroutine factories.
            request_ids: Optional identifiers for each request.

        Returns:
            List of results or exceptions in the same order as inputs.
        """
        if request_ids is None:
            request_ids = [f"req_{i}" for i in range(len(coros))]

        logger.info(f"Processing batch of {len(coros)} requests")

        async def _wrapped(
            coro: Callable[[], Coroutine[Any, Any, T]], req_id: str
        ) -> T:
            try:
                return await self.process_request_with_retry(coro, req_id)
            except Exception as e:
                logger.error(f"[{req_id}] Final failure after all retries: {e}")
                raise

        tasks = [_wrapped(c, rid) for c, rid in zip(coros, request_ids)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"Batch complete: {success}/{len(coros)} succeeded")

        return results

    async def stream_results(
        self,
        coros: list[Callable[[], Coroutine[Any, Any, T]]],
        request_ids: list[str] | None = None,
    ):
        """Stream results as they complete using asyncio.as_completed.

        Yields results in completion order, not input order.

        Args:
            coros: List of coroutine factories.
            request_ids: Optional identifiers for each request.

        Yields:
            Tuples of (request_id, result_or_exception).
        """
        if request_ids is None:
            request_ids = [f"req_{i}" for i in range(len(coros))]

        async def _wrapped(coro: Callable[[], Coroutine[Any, Any, T]], req_id: str):
            try:
                result = await self.process_request_with_retry(coro, req_id)
                return req_id, result
            except Exception as e:
                return req_id, e

        tasks = [
            asyncio.create_task(_wrapped(c, rid)) for c, rid in zip(coros, request_ids)
        ]

        logger.info(f"Streaming {len(tasks)} requests as they complete")

        for completed in asyncio.as_completed(tasks):
            req_id, result = await completed
            yield req_id, result
