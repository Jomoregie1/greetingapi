import os
from fastapi import FastAPI, HTTPException
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.staticfiles import StaticFiles
from redis import asyncio as aioredis
from decouple import config
from app.routers import greeting_routes, greetings_home
from app.routers.config import limiter
from app.exceptions.custom_exceptions import custom_http_exception_handler, ratelimit_exception
from fastapi import Response
from fastapi.openapi.docs import get_swagger_ui_html


def configure_routes(app: FastAPI) -> None:
    app.include_router(greeting_routes.router, prefix="/v1/greetings")
    app.include_router(greetings_home.routers)


def configure_middleware(app: FastAPI) -> None:
    app.add_middleware(SlowAPIMiddleware)


def configure_mounts(app: FastAPI) -> None:
    base_dir = os.path.dirname(os.path.realpath(__file__))
    static_dir = os.path.join(base_dir, 'static')
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


def configure_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, custom_http_exception_handler)
    app.add_exception_handler(RateLimitExceeded, ratelimit_exception)


app = FastAPI()
app.state.limiter = limiter
configure_routes(app)
configure_mounts(app)
configure_middleware(app)
configure_exception_handler(app)


@app.on_event("startup")
async def startup() -> None:
    redis = aioredis.from_url(config('REDIS_URL'))
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# TODO:

# Documentation:
# - Set up automatic interactive API documentation with Swagger UI at /docs and ReDoc at /redoc.
# - Create a custom README or a separate documentation page detailing the API's purpose, setup, and usage instructions.

# Logging:
# - Implement a logging system to track API requests, errors, and significant events for debugging and monitoring.

# Error Handling:
# - Enhance error handling by adding global exception handlers to provide user-friendly error messages.
# - Handle potential errors not yet accounted for in the current setup.

# Testing:
# - Write unit and integration tests for API endpoints and utility functions.
# - Integrate with pytest for testing.
# - Set up continuous integration (CI) to run tests automatically upon code changes.

# Security:
# - Implement authentication and authorization if dealing with sensitive data or expanding API functionality.
# - Add rate limiting to prevent potential abuse.

# Caching:
# - Consider caching mechanisms for improving response times and reducing database load if greetings remain static.

# Deployment:
# - Plan for API deployment to production environments like Heroku, AWS, or DigitalOcean.
# - Ensure security configurations in production, including HTTPS setup.

# Monitoring and Alerts:
# - Integrate with monitoring tools like Grafana, Prometheus, or Sentry for real-time API health checks.
# - Establish alert systems for unexpected issues or downtimes.

# Database Backups:
# - Schedule regular database backups to safeguard against data loss.

# Expand Functionality:
# - Plan for potential future features, e.g., CRUD operations for greetings or analytics on greeting types.

# Feedback Loop:
# - Implement a user feedback system for reporting issues or providing suggestions.

# Rate Limiting and Throttling:
# - Ensure rate limiting is in place to manage request loads and prevent abuse.
