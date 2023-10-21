from sqlalchemy import Column, Integer, Text, VARCHAR, TIMESTAMP, CHAR, Index, event, DDL
from app.database.connection import Base


class Greeting(Base):
    # table name matches the name of an existing table in my database
    __tablename__ = "greetings"

    # Existing names column names to reflect the columns in my table
    greeting_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message = Column(Text(collation="utf8mb4_0900_ai_ci"))
    type = Column(VARCHAR(255), index=True)
    created_at = Column(TIMESTAMP)
    message_hash = Column(CHAR, index=True)

    def __repr__(self):
        return f"Greeting message {self.message} and the type is {self.type}"
