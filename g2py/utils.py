# g2py/utils.py
"""
Utility functions and classes for the G2 API client.
"""

import time
import logging
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .exceptions import (
    G2APIError,
    G2RateLimitError,
    G2AuthenticationError,
    G2ValidationError,
    G2NotFoundError
)
from .config import RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD, RETRY_STATUSES, RETRY_METHODS

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter implementation using token bucket algorithm.
    """
    def __init__(
        self,
        calls: int = RATE_LIMIT_CALLS,
        period: int = RATE_LIMIT_PERIOD
    ):
        self.calls = calls
        self.period = period
        self.tokens = calls
        self.last_check = time.time()

    def wait(self) -> None:
        """
        Wait if necessary to comply with rate limits.
        """
        now = time.time()
        time_passed = now - self.last_check
        self.last_check = now

        # Add tokens for time passed
        self.tokens += time_passed * (self.calls / self.period)
        self.tokens = min(self.tokens, self.calls)

        if self.tokens < 1:
            # Wait until we have at least one token
            sleep_time = (1 - self.tokens) * (self.period / self.calls)
            time.sleep(sleep_time)
            self.tokens = 1

        self.tokens -= 1

def create_retry_session(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Optional[set] = None,
    allowed_methods: Optional[set] = None
) -> requests.Session:
    """
    Create a requests Session with retry functionality.

    Args:
        retries (int): Number of retries
        backoff_factor (float): Backoff factor between retries
        status_forcelist (set): Status codes to retry on
        allowed_methods (set): HTTP methods to retry

    Returns:
        requests.Session: Session with retry configuration
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist or RETRY_STATUSES,
        allowed_methods=allowed_methods or RETRY_METHODS
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

def handle_response(response: requests.Response) -> dict:
    """
    Handle API response and raise appropriate exceptions.

    Args:
        response (requests.Response): Response object

    Returns:
        dict: Parsed JSON response

    Raises:
        G2RateLimitError: When rate limit is exceeded
        G2AuthenticationError: When authentication fails
        G2ValidationError: When request validation fails
        G2NotFoundError: When resource is not found
        G2APIError: For other API errors
    """
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {response.status_code}"
        try:
            error_data = response.json()
            if "errors" in error_data:
                error_msg = error_data["errors"][0].get("detail", error_msg)
        except ValueError:
            pass

        if response.status_code == 429:
            raise G2RateLimitError(error_msg)
        elif response.status_code == 401:
            raise G2AuthenticationError(error_msg)
        elif response.status_code == 422:
            raise G2ValidationError(error_msg)
        elif response.status_code == 404:
            raise G2NotFoundError(error_msg)
        else:
            raise G2APIError(error_msg)

    except ValueError as e:
        raise G2APIError(f"Invalid JSON response: {str(e)}")