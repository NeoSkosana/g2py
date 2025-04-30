import requests
import time
import logging
from typing import Any, Dict, Optional, List, Union
from .exceptions import G2APIError, G2RateLimitError
from .models import Review, Product
from .config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT

logger = logging.getLogger("g2py")

class G2Client:
    def __init__(
        self,
        api_token: str,
        partner_name: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ):
        self.api_token = api_token
        self.partner_name = partner_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Token token={api_token}",
            "Content-Type": "application/vnd.api+json"
        }

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        for attempt in range(self.max_retries):
            try:
                resp = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )
                if resp.status_code == 429:
                    logger.warning("Rate limit hit, sleeping before retry...")
                    time.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.HTTPError as e:
                if resp.status_code == 429:
                    raise G2RateLimitError("Rate limit exceeded") from e
                logger.error(f"HTTP error: {e}")
                raise G2APIError(f"API error: {e}") from e
            except Exception as e:
                logger.error(f"Request failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise G2APIError("Max retries exceeded")

    # Example: Get reviews for a product
    def get_reviews(self, product_id: str, page: int = 1, per_page: int = 100) -> List[Review]:
        params = {
            "filter[product_id]": product_id,
            "page[size]": min(per_page, 100),
            "page[number]": page
        }
        data = self._request("GET", "reviews", params=params)
        return [Review.from_api(r) for r in data.get("data", [])]

    # Example: Get all reviews with pagination
    def get_all_reviews(self, product_id: str) -> List[Review]:
        reviews = []
        page = 1
        while True:
            batch = self.get_reviews(product_id, page=page)
            if not batch:
                break
            reviews.extend(batch)
            page += 1
        return reviews

    # Add more methods for products, categories, etc.

    # Example: Get product details
    def get_product(self, product_id: str) -> Product:
        data = self._request("GET", f"products/{product_id}")
        return Product.from_api(data["data"])

    # Example: Get categories
    def get_categories(self) -> List[Dict]:
        data = self._request("GET", "categories")
        return data.get("data", [])

    # ... more endpoints as needed