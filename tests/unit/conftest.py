import asyncio
from typing import Generator

import pytest
import pytest_asyncio
from decouple import config
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, HTTPStatusError
from app.models.greeting import Greeting
from app.routers.greeting_routes import get_db
from app.database.connection import Base
from app.main import app

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
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
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


# This is overriding the dependency for get_db with override_get_db.
app.dependency_overrides[get_db] = override_get_db
