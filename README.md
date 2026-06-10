# USPS 1oz Letter Stamp Price API

A FastAPI application that scrapes the official USPS Notice 123 and serves the price using **HTMX hypermedia**. The index page loads the price dynamically via HTMX, receiving HTML fragments from the server rather than JSON.

## Current Price

The API currently returns **$0.78** per 1oz letter stamp (as of the latest Notice 123 effective date).

## How It Works

1. Scrapes `https://pe.usps.com/text/dmm300/Notice123.htm` (the official USPS price list)
2. Parses the "Letters (Stamped)" section under First-Class Mail Retail Prices
3. Extracts the 1oz letter price (the first row in the table)
4. Caches the result for 24 hours (since the price rarely changes)
5. **Serves the price as HTML fragments (hypermedia) via HTMX**

## Architecture: HTMX + Hypermedia

This application uses **HTMX** for the frontend, which means:

- The browser loads a minimal HTML page with HTMX from CDN
- HTMX automatically fetches `/price` on page load
- The server returns an **HTML fragment** (not JSON)
- HTMX swaps the fragment into the page

This is a **hypermedia-driven architecture** (HATEOAS) where the server returns HTML, and the client updates the DOM directly.

### Content Negotiation

The `/price` endpoint supports content negotiation:

- **HTML request** (`Accept: text/html`) - Returns an HTML fragment for HTMX
- **JSON request** (`Accept: application/json`) - Returns JSON for API clients

## Project Structure

```
uspost_al/
├── __init__.py       # Package initialization
├── config.py          # Application configuration (immutable dataclass)
├── cache.py           # Price caching layer with TTL
├── client.py          # HTTP client for Notice 123
├── parser.py          # HTML parsing logic
├── service.py         # Business logic service layer
└── routes.py          # FastAPI routes and HTML templates

main.py               # Application entry point (factory pattern)
pyproject.toml        # UV project configuration
uv.lock               # Locked dependency versions
```

### Separation of Concerns

- **config.py**: Immutable configuration via `dataclass`
- **cache.py**: TTL-based caching with `PriceInfo` data class
- **client.py**: HTTP client abstraction (can be swapped/mocked)
- **parser.py**: HTML parsing with multiple strategies
- **service.py**: Business logic, orchestrates client + parser + cache
- **routes.py**: HTTP layer, templates, content negotiation
- **main.py**: Application factory, dependency injection

## Running the API

### Using UV (recommended)

```bash
# Install dependencies
uv sync

# Run the application
uv run python main.py
```

The API will be available at `http://localhost:8000`

### Alternative: Direct Uvicorn

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

| Endpoint | Method | Description | Response Type |
|----------|--------|-------------|---------------|
| `/` | GET | **Index page** - Loads HTMX and fetches price dynamically | HTML |
| `/price` | GET | **Price fragment** - Returns HTML fragment for HTMX, or JSON if requested | HTML/JSON |
| `/stamp-price` | GET | **JSON API** - Returns price in JSON format | JSON |
| `/health` | GET | Health check and cache status | JSON |
| `/docs` | GET | Auto-generated Swagger documentation | HTML |

## HTMX Example

The index page (`/`) contains:

```html
<div id="price-display"
     hx-get="/price"
     hx-trigger="load"
     hx-swap="outerHTML">
    Loading price...
</div>
```

On page load, HTMX sends a `GET /price` request. The server returns:

```html
<div class="price-container">
    <div class="price">
        <span class="currency">$</span>0.78
    </div>
    <div class="subtitle">USPS 1oz Letter Stamp</div>
    <div class="source">Source: USPS Notice 123</div>
</div>
```

HTMX swaps this into the page, replacing the loading message.

## Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- BeautifulSoup4 - HTML parsing
- Requests - HTTP client
- lxml - HTML parser backend
- HTMX (loaded via CDN) - Frontend hypermedia library

## Notes

- The 1oz letter stamp price is the First-Class Mail 1-oz letter retail price
- Notice 123 is updated periodically (usually annually or semi-annually)
- The API pre-fetches the price on startup and caches it for 24 hours
- If the USPS website is unavailable, the API returns a 503 error
- The API only looks for the 1oz letter price, not metered rates or other services
- HTMX is loaded from CDN (`https://unpkg.com/htmx.org@1.9.12`)

## Running Tests

```bash
# Test the service layer
uv run python -c "from uspost_al.service import StampPriceService; from uspost_al.config import get_config; s = StampPriceService.from_config(get_config()); print(s.get_price())"

# Test the parser
uv run python -c "from uspost_al.parser import Notice123Parser; from uspost_al.client import Notice123Client; from uspost_al.config import get_config; c = get_config(); p = Notice123Parser(c); html = Notice123Client(c).fetch(); print(p.parse(html))"
```
