import asyncio
from typing import Generator
import pytest
import pytest_asyncio
from decouple import config
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, HTTPStatusError
from app.models.greeting import Greeting
from app.routers.greeting_routes import get_db
from app.database.connection import Base
from app.main import app, configure_routes, configure_middleware, configure_exception_handler

DATABASE_URL = config('TEST_DATABASE_URL')
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncTestSessionLocal = sessionmaker(bind=engine,
                                     expire_on_commit=False,
                                     class_=AsyncSession,
                                     autoflush=False,
                                     autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def initialize_cache():
    loop = asyncio.get_event_loop()
    redis_url = config('REDIS_URL')
    redis = loop.run_until_complete(aioredis.from_url(redis_url))
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    loop.run_until_complete(redis.aclose())


# # Test client allows you to send http requests to your fastapi application to recieve responses.
@pytest_asyncio.fixture(scope="function")
async def async_client_with_rate_limiter():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


def create_test_limiter():
    limiter = Limiter(key_func=get_remote_address, enabled=False)
    return limiter


@pytest_asyncio.fixture(scope="function")
async def async_client_no_rate_limit():
    # Create a new FastAPI application instance for testing
    test_app = FastAPI()

    # Apply configurations
    configure_routes(test_app)
    configure_middleware(test_app)
    configure_exception_handler(test_app)

    overide_database_dependency(test_app)

    # Disable or modify the rate limiter
    test_app.state.limiter = create_test_limiter()

    async with AsyncClient(app=test_app, base_url="http://testserver") as client:
        yield client


# This is our test database, the following function defines a context manager function, which manages the lifecycle
# of our database session.
async def override_get_db():
    async with AsyncTestSessionLocal() as session:
        yield session


# Responsible for creating all tables and dropping all tables
@pytest_asyncio.fixture()
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Generates a list of greetings
def get_greetings(greeting_type, count):
    return [Greeting(message=f"Test Message {i}", type=greeting_type) for i in range(count)]


# adds list of greetings to database one by one.
async def add_greetings_to_db(greetings):
    async with AsyncTestSessionLocal() as db:
        async with db.begin():
            for greeting in greetings:
                db.add(greeting)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def overide_database_dependency(app):
    app.dependency_overrides[get_db] = override_get_db


overide_database_dependency(app)
