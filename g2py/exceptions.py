# g2py/exceptions.py
"""Custom exceptions for the G2Py client."""

class G2APIError(Exception):
    """Base exception for G2 API errors."""
    def __init__(self, message: str, response=None):
        super().__init__(message)
        self.response = response

class G2RateLimitError(G2APIError):
    """Raised when API rate limit is exceeded."""
    pass

class G2AuthenticationError(G2APIError):
    """Raised when authentication fails."""
    pass

class G2ValidationError(G2APIError):
    """Raised when request validation fails."""
    pass

class G2NotFoundError(G2APIError):
    """Raised when a resource is not found."""
    pass

class G2ConnectionError(G2APIError):
    """Raised when connection to G2 API fails."""
    pass

class G2TimeoutError(G2APIError):
    """Raised when request times out."""
    pass

class G2CacheError(Exception):
    """Raised when cache operations fail."""
    pass