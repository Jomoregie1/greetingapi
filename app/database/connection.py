from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# Uses config to retrieve the database url from .env file
DATABASE_URL = config('MAIN_DATABASE_URL')

# Creates an engine to manage database connection to excute queries
engine = create_async_engine(DATABASE_URL)

# Creates a factory for creating new databse sessions.
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)
# This creates a new base class for my models, which allows me to define tables and python classes
Base = declarative_base()
