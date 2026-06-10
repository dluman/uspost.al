"""Application configuration and settings."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Immutable application configuration."""
    
    # USPS Notice 123 URL
    notice_123_url: str = "https://pe.usps.com/text/dmm300/Notice123.htm"
    
    # Cache TTL in hours
    cache_ttl_hours: int = 24
    
    # HTTP request headers
    request_headers: dict = None
    
    # HTTP timeout in seconds
    request_timeout: int = 30
    
    # Price sanity check bounds
    min_price: float = 0.50
    max_price: float = 2.00
    
    def __post_init__(self):
        # Set default headers if not provided
        if self.request_headers is None:
            object.__setattr__(
                self,
                'request_headers',
                {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                }
            )


def get_config() -> Config:
    """Get the application configuration."""
    return Config()
