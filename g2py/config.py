# g2py/config.py
"""Configuration settings for the G2Py client."""

from typing import Dict, Any
import os

# API Configuration
DEFAULT_BASE_URL = "https://data.g2.com/api/v1"
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_BATCH_SIZE = 100

# Rate Limiting
RATE_LIMIT_CALLS = 100  # calls
RATE_LIMIT_PERIOD = 1  # seconds

# Retry Configuration
RETRY_STATUSES = {408, 429, 500, 502, 503, 504}
RETRY_METHODS = {'GET', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'}

# Cache Configuration
DEFAULT_CACHE_TTL = 300  # seconds
DEFAULT_CACHE_ENABLED = False

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

class G2Config:
    """Configuration class for G2Py client."""

    def __init__(self, **kwargs: Dict[str, Any]):
        self.base_url = kwargs.get('base_url', DEFAULT_BASE_URL)
        self.timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
        self.max_retries = kwargs.get('max_retries', DEFAULT_MAX_RETRIES)
        self.batch_size = kwargs.get('batch_size', DEFAULT_BATCH_SIZE)
        self.cache_ttl = kwargs.get('cache_ttl', DEFAULT_CACHE_TTL)
        self.cache_enabled = kwargs.get('cache_enabled', DEFAULT_CACHE_ENABLED)

        # Load environment variables if available
        self.api_token = kwargs.get('api_token') or os.getenv('G2_API_TOKEN')
        self.partner_name = kwargs.get('partner_name') or os.getenv('G2_PARTNER_NAME')

        if not self.api_token:
            raise ValueError("API token must be provided either through kwargs or G2_API_TOKEN environment variable")