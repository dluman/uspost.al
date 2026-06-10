"""Business logic service layer for stamp price retrieval."""

import logging
from typing import Optional

from uspost_al.cache import PriceCache
from uspost_al.client import Notice123Client
from uspost_al.config import Config
from uspost_al.parser import Notice123Parser

logger = logging.getLogger(__name__)


class StampPriceService:
    """Service for retrieving and caching stamp prices."""
    
    def __init__(
        self,
        config: Config,
        client: Notice123Client,
        parser: Notice123Parser,
        cache: PriceCache,
    ):
        self._config = config
        self._client = client
        self._parser = parser
        self._cache = cache
    
    @classmethod
    def from_config(cls, config: Config) -> "StampPriceService":
        """Factory method to create service from config."""
        return cls(
            config=config,
            client=Notice123Client(config),
            parser=Notice123Parser(config),
            cache=PriceCache(config.cache_ttl_hours),
        )
    
    def get_price(self) -> Optional[dict]:
        """
        Get the current 1oz letter stamp price.
        
        Returns cached value if available, otherwise fetches and parses Notice 123.
        """
        # Check cache first
        cached = self._cache.get()
        if cached:
            logger.info("Returning cached 1oz letter price")
            return cached.to_dict()
        
        # Fetch fresh data
        html = self._client.fetch()
        if not html:
            return None
        
        price = self._parser.parse(html)
        if price is None:
            return None
        
        # Store in cache
        self._cache.set(price, self._config.notice_123_url)
        
        return self._cache.get().to_dict()
    
    def health_check(self) -> dict:
        """Return health status of the service."""
        return {
            "status": "healthy" if self._cache.is_cached() else "no_cache",
            "cached": self._cache.is_cached(),
            "cache_age_seconds": self._cache.cache_age_seconds(),
        }
    
    def warm_cache(self) -> Optional[dict]:
        """Pre-fetch the price to warm the cache."""
        price_info = self.get_price()
        if price_info:
            logger.info(f"Pre-fetched 1oz letter price: ${price_info['price']:.2f}")
        else:
            logger.warning("Failed to pre-fetch 1oz letter price")
        return price_info
