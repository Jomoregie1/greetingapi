from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException


# Request is the incoming request that caused the exception and exc the exception instance that was raised.
# Purpose of custom exception is to handle, 422 errors, where uses has not given any type.
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 422:
        return JSONResponse(
            status_code=400,
            content={"detail": "The 'type' query parameter is required."}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def ratelimit_exception(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={'detail': "Too Many Requests"})


