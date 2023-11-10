from sqlalchemy import Column, Integer, Text, VARCHAR, TIMESTAMP, CHAR, DDL, event
from sqlalchemy.ext.declarative import declarative_base
from app.database.connection import Base


class Greeting(Base):
    # table name matches the name of an existing table in my database
    __tablename__ = "greetings"

    # Existing names column names to reflect the columns in my table
    greeting_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message = Column(Text(collation="utf8mb4_0900_ai_ci"))
    type = Column(VARCHAR(255), index=True)
    created_at = Column(TIMESTAMP)
    message_hash = Column(CHAR(64), index=True)

    def __repr__(self):
        return f"Greeting message {self.message} and the type is {self.type}"


fulltext_index = DDL("ALTER TABLE greetings ADD FULLTEXT(message)")

event.listen(
    Greeting.__table__,
    'after_create',
    fulltext_index.execute_if(dialect='mysql')

)
