"""Application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from uspost_al.config import get_config
from uspost_al.routes import create_router
from uspost_al.service import StampPriceService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Application factory.
    
    Creates and configures the FastAPI application with all dependencies.
    """
    config = get_config()
    service = StampPriceService.from_config(config)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan context manager for startup/shutdown events."""
        logger.info("Starting up 1oz Letter Stamp Price API")
        # Pre-fetch on startup
        service.warm_cache()
        yield
        logger.info("Shutting down 1oz Letter Stamp Price API")
    
    app = FastAPI(
        title="USPS 1oz Letter Stamp Price API",
        description="Returns the current USPS 1oz letter stamp price scraped from Notice 123",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Include all routes
    router = create_router(service)
    app.include_router(router)
    
    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
