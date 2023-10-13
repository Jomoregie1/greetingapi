from sqlalchemy import Column, Integer, Text, VARCHAR, TIMESTAMP, CHAR
from app.database.connection import Base


class Greeting(Base):
    # table name matches the name of an existing table in my database
    __tablename__ = "greetings"

    # Existing names column names to relect the columns in my table
    greeting_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message = Column(Text, index=True)
    type = Column(VARCHAR, index=True)
    created_at = Column(TIMESTAMP)
    message_hash = Column(CHAR, index=True)
