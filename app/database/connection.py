from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# Uses config to retrieve the database url from .env file
DATABASE_URL = config('DATABASE_URL')

# Creates an engine to manage database connection to excute queries
engine = create_engine(DATABASE_URL)

# Creates a factory for creating new databse sessions.
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# This creates a new base class for my models, which allows me to define tables and python classes
Base = declarative_base()
