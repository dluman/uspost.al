"""HTTP client for fetching USPS Notice 123."""

import logging
from typing import Optional

import requests

from uspost_al.config import Config

logger = logging.getLogger(__name__)


class Notice123Client:
    """Client for fetching USPS Notice 123 HTML content."""
    
    def __init__(self, config: Config):
        self._config = config
    
    def fetch(self) -> Optional[str]:
        """Fetch the Notice 123 HTML content."""
        try:
            response = requests.get(
                self._config.notice_123_url,
                headers=self._config.request_headers,
                timeout=self._config.request_timeout,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch Notice 123: {e}")
            return None
