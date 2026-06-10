"""Price caching layer."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class PriceInfo:
    """Data class for price information."""
    price: float
    currency: str
    last_updated: datetime
    source: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "price": self.price,
            "currency": self.currency,
            "last_updated": self.last_updated.isoformat(),
            "source": self.source,
        }


class PriceCache:
    """Thread-safe price cache with TTL support."""
    
    def __init__(self, ttl_hours: int = 24):
        self._ttl = timedelta(hours=ttl_hours)
        self._price_info: Optional[PriceInfo] = None
    
    def get(self) -> Optional[PriceInfo]:
        """Get cached price if not expired."""
        if self._price_info is None:
            return None
        
        if datetime.now() - self._price_info.last_updated > self._ttl:
            self._price_info = None
            return None
        
        return self._price_info
    
    def set(self, price: float, source: str) -> None:
        """Store price in cache."""
        self._price_info = PriceInfo(
            price=price,
            currency="USD",
            last_updated=datetime.now(),
            source=source,
        )
    
    def is_cached(self) -> bool:
        """Check if a valid cached entry exists."""
        return self.get() is not None
    
    def cache_age_seconds(self) -> Optional[float]:
        """Get age of cached entry in seconds."""
        if self._price_info is None:
            return None
        return (datetime.now() - self._price_info.last_updated).total_seconds()
