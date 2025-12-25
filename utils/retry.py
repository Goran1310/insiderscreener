"""
Retry utilities with exponential backoff
"""

import asyncio
import functools
from typing import TypeVar, Callable, Any
from config import SCRAPER_CONFIG
from .logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


def retry_async(
    max_attempts: int = None,
    base_delay: float = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for async functions with retry logic and exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts (default from config)
        base_delay: Base delay for exponential backoff in seconds (default from config)
        exceptions: Tuple of exception types to catch and retry
        
    Example:
        @retry_async(max_attempts=3, base_delay=2)
        async def scrape_data(url):
            # Your scraping logic
            pass
    """
    if max_attempts is None:
        max_attempts = SCRAPER_CONFIG["retry_attempts"]
    if base_delay is None:
        base_delay = SCRAPER_CONFIG["retry_delay_base"]
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {str(e)}"
                        )
                        raise
                    
                    # Calculate exponential backoff delay
                    delay = base_delay ** attempt
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {str(e)}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    
                    await asyncio.sleep(delay)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


async def retry_with_timeout(
    coro: Callable,
    timeout: float = None,
    max_attempts: int = None,
    base_delay: float = None
) -> Any:
    """
    Execute an async coroutine with timeout and retry logic
    
    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds (default from config)
        max_attempts: Maximum retry attempts
        base_delay: Base delay for exponential backoff
        
    Returns:
        Result of the coroutine
        
    Raises:
        asyncio.TimeoutError: If operation times out
        Exception: If all retry attempts fail
    """
    if timeout is None:
        timeout = SCRAPER_CONFIG["timeout"] / 1000  # Convert ms to seconds
    if max_attempts is None:
        max_attempts = SCRAPER_CONFIG["retry_attempts"]
    if base_delay is None:
        base_delay = SCRAPER_CONFIG["retry_delay_base"]
    
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except (asyncio.TimeoutError, Exception) as e:
            last_exception = e
            
            if attempt == max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts: {str(e)}")
                raise
            
            delay = base_delay ** attempt
            logger.warning(
                f"Attempt {attempt}/{max_attempts} failed: {str(e)}. "
                f"Retrying in {delay:.1f}s..."
            )
            await asyncio.sleep(delay)
    
    if last_exception:
        raise last_exception
