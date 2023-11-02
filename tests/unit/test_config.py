from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from app.models.greeting import Greeting
from app.routers.greeting_routes import get_db
from app.main import app

DATABASE_URL = config('TEST_DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test client allows you to send http requests to your fastapi application to recieve responses.
client = TestClient(app)


# This is our test database, the following function defines a context manager function, which manages the lifecycle
# of our database session.
def override_get_db():
    # try and except used to ensure cleanup action.
    db = TestSessionLocal()
    try:
        # makes the function a generator based context manager allowing it to use the session to make database queries
        yield db
    finally:
        db.close()


# Utility function to add a given number of greetings to the database for a given test.
def add_greetings_to_db(greeting_type, count, db_session):
    greetings = [
        Greeting(message=f"Message {i}", type=greeting_type) for i in range(count)
    ]
    db_session.bulk_save_objects(greetings)
    db_session.commit()


# This is overriding the dependency for get_db with override_get_db.
app.dependency_overrides[get_db] = override_get_db
