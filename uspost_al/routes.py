"""FastAPI routes and HTML templates."""

from fastapi import APIRouter, Header
from fastapi.responses import HTMLResponse, JSONResponse

from uspost_al.service import StampPriceService

# HTML Templates
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USPS 1oz Letter Stamp Price</title>
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        .container {{
            text-align: center;
        }}
        .price {{
            font-size: 20vw;
            font-weight: bold;
            color: #333333;
            line-height: 1;
            margin: 0;
        }}
        .currency {{
            font-size: 10vw;
            color: #666666;
            vertical-align: super;
        }}
        .subtitle {{
            font-size: 1.5rem;
            color: #999999;
            margin-top: 2rem;
        }}
        .source {{
            font-size: 0.9rem;
            color: #cccccc;
            margin-top: 1rem;
        }}
        .error {{
            color: #cc0000;
        }}
        .loading {{
            font-size: 5vw;
            color: #cccccc;
        }}
    </style>
</head>
<body>
    <div class="container" id="price-display"
         hx-get="/price"
         hx-trigger="load"
         hx-swap="outerHTML">
        <div class="loading">Loading price...</div>
    </div>
</body>
</html>
"""

PRICE_FRAGMENT = """
<div class="price-container">
    <div class="price">
        <span class="currency">$</span>{price:.2f}
    </div>
    <div class="subtitle">USPS 1oz Letter Stamp</div>
    <div class="source">Source: USPS Notice 123</div>
</div>
"""

ERROR_FRAGMENT = """
<div class="price-container">
    <div class="price error">--.--</div>
    <div class="subtitle">USPS 1oz Letter Stamp</div>
    <div class="source error">Unable to fetch price from USPS Notice 123</div>
</div>
"""


def create_router(service: StampPriceService) -> APIRouter:
    """Create the API router with all endpoints."""
    router = APIRouter()
    
    @router.get("/", response_class=HTMLResponse)
    async def root():
        """
        Return the index page with HTMX.
        HTMX will automatically fetch /price on page load and swap the content.
        """
        return HTMLResponse(INDEX_TEMPLATE)
    
    @router.get("/price", response_class=HTMLResponse)
    async def price_fragment(accept: str = Header(None)):
        """
        Return the price as an HTML fragment (hypermedia for HTMX).
        
        HTMX requests include Accept: text/html by default.
        If the client requests JSON (Accept: application/json), return JSON instead.
        """
        price_info = service.get_price()
        
        if price_info is None:
            if accept and "application/json" in accept:
                return JSONResponse(
                    status_code=503,
                    content={"error": "Unable to fetch 1oz letter stamp price from USPS Notice 123"},
                )
            return HTMLResponse(ERROR_FRAGMENT, status_code=503)
        
        if accept and "application/json" in accept:
            return JSONResponse(price_info)
        
        return HTMLResponse(PRICE_FRAGMENT.format(price=price_info["price"]))
    
    @router.get("/stamp-price")
    async def stamp_price():
        """JSON API endpoint for programmatic access."""
        price_info = service.get_price()
        if price_info is None:
            return JSONResponse(
                status_code=503,
                content={"error": "Unable to fetch 1oz letter stamp price from USPS Notice 123"},
            )
        return price_info
    
    @router.get("/health")
    async def health():
        """Health check endpoint."""
        return service.health_check()
    
    return router
