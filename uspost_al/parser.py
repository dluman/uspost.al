"""HTML parser for extracting 1oz letter stamp price from Notice 123."""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from uspost_al.config import Config

logger = logging.getLogger(__name__)


class Notice123Parser:
    """Parser for extracting stamp price from Notice 123 HTML."""
    
    def __init__(self, config: Config):
        self._config = config
    
    def parse(self, html: str) -> Optional[float]:
        """
        Parse Notice 123 HTML to find the 1oz letter stamp price.
        
        Returns:
            The price as a float, or None if not found.
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Try each parsing strategy in order
        price = (
            self._parse_letters_stamped_section(soup)
            or self._parse_retail_section(soup)
        )
        
        if price is None:
            logger.error("Could not parse 1oz letter price from Notice 123")
        
        return price
    
    def _parse_letters_stamped_section(self, soup: BeautifulSoup) -> Optional[float]:
        """Parse the 'Letters (Stamped)' section for the 1oz price."""
        for section in soup.find_all(["h4", "h3", "h5", "h2"]):
            section_text = section.get_text().strip()
            if "Letters (Stamped)" in section_text:
                table = section.find_next("table")
                if table:
                    return self._extract_1oz_price_from_table(table)
        return None
    
    def _parse_retail_section(self, soup: BeautifulSoup) -> Optional[float]:
        """Parse the 'Retail Prices' -> 'First-Class Mail' section."""
        in_retail_section = False
        for elem in soup.find_all(["h2", "h3", "h4", "h5", "h6", "p", "div", "table"]):
            text = elem.get_text().strip()
            if "Retail Prices" in text and "First-Class" in text:
                in_retail_section = True
            if in_retail_section and elem.name == "table":
                table_text = elem.get_text()
                if "Letters" in table_text and "$" in table_text:
                    return self._extract_1oz_price_from_table(elem)
        return None
    
    def _extract_1oz_price_from_table(self, table) -> Optional[float]:
        """Extract the 1oz price from a table element."""
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            
            first_cell = cells[0].get_text().strip()
            if first_cell == "1" or "1 oz" in first_cell or "1 ounce" in first_cell:
                for cell in cells[1:]:
                    cell_text = cell.get_text().strip()
                    price_match = re.search(r"\$([0-9]+\.[0-9]{2})", cell_text)
                    if price_match:
                        price = float(price_match.group(1))
                        if self._is_valid_price(price):
                            return price
        return None
    
    def _is_valid_price(self, price: float) -> bool:
        """Validate that the price is within expected bounds."""
        return self._config.min_price <= price <= self._config.max_price
