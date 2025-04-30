# g2py/models.py
"""Data models for G2 API responses."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class Review:
    """Represents a G2 review."""
    id: str
    title: str
    content: str
    rating: float
    pros: Optional[str]
    cons: Optional[str]
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    reviewer_name: Optional[str]
    product_id: str

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Review':
        """Create a Review instance from API response data."""
        attrs = data.get('attributes', {})
        return cls(
            id=data.get('id'),
            title=attrs.get('title', ''),
            content=attrs.get('content', ''),
            rating=float(attrs.get('rating', 0.0)),
            pros=attrs.get('pros'),
            cons=attrs.get('cons'),
            status=ReviewStatus(attrs.get('status', 'pending')),
            created_at=datetime.fromisoformat(attrs.get('created_at')),
            updated_at=datetime.fromisoformat(attrs.get('updated_at')),
            reviewer_name=attrs.get('reviewer_name'),
            product_id=attrs.get('product_id')
        )

@dataclass
class Product:
    """Represents a G2 product."""
    id: str
    name: str
    description: Optional[str]
    website: Optional[str]
    categories: List[str]
    average_rating: float
    review_count: int

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Product':
        """Create a Product instance from API response data."""
        attrs = data.get('attributes', {})
        return cls(
            id=data.get('id'),
            name=attrs.get('name', ''),
            description=attrs.get('description'),
            website=attrs.get('website'),
            categories=attrs.get('categories', []),
            average_rating=float(attrs.get('average_rating', 0.0)),
            review_count=int(attrs.get('review_count', 0))
        )

@dataclass
class Category:
    """Represents a G2 category."""
    id: str
    name: str
    description: Optional[str]
    product_count: int

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Category':
        """Create a Category instance from API response data."""
        attrs = data.get('attributes', {})
        return cls(
            id=data.get('id'),
            name=attrs.get('name', ''),
            description=attrs.get('description'),
            product_count=int(attrs.get('product_count', 0))
        )