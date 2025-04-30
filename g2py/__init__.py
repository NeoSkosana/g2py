# g2py/__init__.py
"""
G2Py - A Production-Grade Python Wrapper for the G2 API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A robust, async-capable Python client for the G2 API.
Features include automatic retries, rate limiting, pagination,
and both sync and async support.

Basic usage:
    >>> from g2py import G2Client
    >>> client = G2Client(api_token="your-token")
    >>> reviews = client.get_reviews("product-id")

For async usage:
    >>> from g2py import AsyncG2Client
    >>> async with AsyncG2Client(api_token="your-token") as client:
    ...     reviews = await client.get_reviews("product-id")
"""

from .client import G2Client
from .async_client import AsyncG2Client
from .exceptions import (
    G2APIError,
    G2RateLimitError,
    G2AuthenticationError,
    G2ValidationError
)
from .models import Review, Product, Category

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    "G2Client",
    "AsyncG2Client",
    "G2APIError",
    "G2RateLimitError",
    "G2AuthenticationError",
    "G2ValidationError",
    "Review",
    "Product",
    "Category"
]