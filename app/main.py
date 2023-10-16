from fastapi import FastAPI, HTTPException
from app.routers import greeting_routes
from app.exceptions.custom_exceptions import custom_http_exception_handler

app = FastAPI()
app.include_router(greeting_routes.router, prefix="/v1/greetings")
app.add_exception_handler(HTTPException, custom_http_exception_handler)

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
