# g2py/client.py
"""
Synchronous G2 API client implementation.
"""

import logging
import time
from typing import Optional, List, Dict, Any, Union, Iterator
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .config import G2Config
from .exceptions import (
    G2APIError,
    G2RateLimitError,
    G2AuthenticationError,
    G2ValidationError,
    G2NotFoundError,
    G2ConnectionError,
    G2TimeoutError
)
from .models import Review, Product, Category
from .utils import RateLimiter, create_retry_session, handle_response

logger = logging.getLogger(__name__)

class G2Client:
    """
    Synchronous G2 API client with built-in retry, rate limiting, and pagination.

    Args:
        api_token (str): G2 API authentication token
        partner_name (str, optional): G2 partner name for review collection
        config (G2Config, optional): Configuration object
        session (requests.Session, optional): Custom session object

    Usage:
        >>> client = G2Client(api_token="your-token")
        >>> reviews = client.get_reviews("product-id")
        >>> for review in reviews:
        ...     print(review.title)
    """

    def __init__(
        self,
        api_token: str,
        partner_name: Optional[str] = None,
        config: Optional[G2Config] = None,
        session: Optional[requests.Session] = None
    ):
        self.config = config or G2Config(api_token=api_token, partner_name=partner_name)
        self.session = session or create_retry_session()
        self.rate_limiter = RateLimiter()

        # Set up authentication and headers
        self.headers = {
            "Authorization": f"Token token={self.config.api_token}",
            "Content-Type": "application/vnd.api+json",
            "User-Agent": f"g2py/{self.__version__}"
        }

    @property
    def __version__(self) -> str:
        """Return package version."""
        from . import __version__
        return __version__

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the G2 API.

        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            data (dict, optional): Request body
            **kwargs: Additional arguments passed to requests

        Returns:
            dict: Parsed JSON response

        Raises:
            G2APIError: Base class for all API errors
            G2RateLimitError: When rate limit is exceeded
            G2AuthenticationError: When authentication fails
            G2ValidationError: When request validation fails
            G2NotFoundError: When resource is not found
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        # Wait for rate limit
        self.rate_limiter.wait()

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=self.config.timeout,
                **kwargs
            )

            return handle_response(response)

        except requests.exceptions.Timeout as e:
            raise G2TimeoutError(f"Request timed out: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise G2ConnectionError(f"Connection failed: {str(e)}")
        except Exception as e:
            raise G2APIError(f"Unexpected error: {str(e)}")

    def get_reviews(
        self,
        product_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 100,
        updated_since: Optional[str] = None
    ) -> List[Review]:
        """
        Get reviews, optionally filtered by product and date.

        Args:
            product_id (str, optional): Filter by product ID
            page (int): Page number for pagination
            per_page (int): Results per page (max 100)
            updated_since (str, optional): ISO format datetime

        Returns:
            List[Review]: List of Review objects
        """
        params = {
            "page[size]": min(per_page, 100),
            "page[number]": page
        }

        if product_id:
            params["filter[product_id]"] = product_id
        if updated_since:
            params["filter[updated_at_gt]"] = updated_since

        data = self._request("GET", "reviews", params=params)
        return [Review.from_api(review) for review in data.get("data", [])]

    def get_all_reviews(
        self,
        product_id: Optional[str] = None,
        updated_since: Optional[str] = None
    ) -> Iterator[Review]:
        """
        Get all reviews using pagination.

        Args:
            product_id (str, optional): Filter by product ID
            updated_since (str, optional): ISO format datetime

        Returns:
            Iterator[Review]: Iterator of Review objects
        """
        page = 1
        while True:
            reviews = self.get_reviews(
                product_id=product_id,
                page=page,
                updated_since=updated_since
            )
            if not reviews:
                break
            yield from reviews
            page += 1

    def get_product(self, product_id: str) -> Product:
        """
        Get detailed information about a product.

        Args:
            product_id (str): G2 product ID

        Returns:
            Product: Product object
        """
        data = self._request("GET", f"products/{product_id}")
        return Product.from_api(data["data"])

    def get_categories(self, page: int = 1, per_page: int = 100) -> List[Category]:
        """
        Get list of G2 product categories.

        Args:
            page (int): Page number for pagination
            per_page (int): Results per page (max 100)

        Returns:
            List[Category]: List of Category objects
        """
        params = {
            "page[size]": min(per_page, 100),
            "page[number]": page
        }
        data = self._request("GET", "categories", params=params)
        return [Category.from_api(category) for category in data.get("data", [])]

    def get_review_form_token(self, product_id: str) -> str:
        """
        Get a review form access token.

        Args:
            product_id (str): G2 product ID

        Returns:
            str: Review form access token
        """
        if not self.config.partner_name:
            raise ValueError("Partner name required for review collection")

        response = self._request(
            "POST",
            f"partnerships/{self.config.partner_name}/tokens",
            params={
                "product_id": product_id
            }
        )
        return response["state"]

    def get_review_form_url(self, product_id: str, email: str) -> str:
        """
        Generate a review form URL for a user.

        Args:
            product_id (str): G2 product ID
            email (str): User's email address

        Returns:
            str: Complete review form URL
        """
        token = self.get_review_form_token(product_id)
        encoded_email = quote(email)
        return (
            f"https://www.g2.com/partnerships/{self.config.partner_name}/"
            f"users/login.embed?state={token}&email={encoded_email}"
        )

    def analyze_product_sentiment(self, product_id: str) -> Dict[str, Any]:
        """
        Analyze sentiment of product reviews.

        Args:
            product_id (str): Product ID to analyze

        Returns:
            Dict[str, Any]: Sentiment analysis results
        """
        reviews = list(self.get_all_reviews(product_id))
        if not reviews:
            return {
                "average_rating": 0.0,
                "total_reviews": 0,
                "sentiment_distribution": {},
                "negative_reviews": 0,
                "positive_reviews": 0
            }

        ratings = [review.rating for review in reviews]

        return {
            "average_rating": sum(ratings) / len(ratings),
            "total_reviews": len(ratings),
            "sentiment_distribution": {
                "1": len([r for r in ratings if r == 1]),
                "2": len([r for r in ratings if r == 2]),
                "3": len([r for r in ratings if r == 3]),
                "4": len([r for r in ratings if r == 4]),
                "5": len([r for r in ratings if r == 5])
            },
            "negative_reviews": len([r for r in ratings if r <= 3]),
            "positive_reviews": len([r for r in ratings if r > 3])
        }