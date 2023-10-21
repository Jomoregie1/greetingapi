import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers.greeting_routes import get_db
from app.models.greeting import Greeting
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from decouple import config

# Using testclient allows me to simulate HTTP requests to my application in isolation.
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = config('TEST_DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# TODO database issue fixed, comment code and add more test, to test get_greetings endpoint.

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


# fixture used in setting up and tearing down of the database
@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# This is overriding the dependency for get_db with override_get_db.
app.dependency_overrides[get_db] = override_get_db

# Test client allows you to send http requests to your fastapi application to recieve responses.
client = TestClient(app)


def test_get_greetings_sucess(test_db):
    db = TestSessionLocal()
    greeting = Greeting(message="Hello, World!", type='birthday_boyfriend_message')
    db.add(greeting)
    db.commit()
    db.close()

    response = client.get('/v1/greetings/?type=Birthday_Boyfriend')
    greeting = response.json()[0]
    assert response.status_code == 200
    assert greeting['message'] == "Hello, World!"


def test_filter_greetings_by_type(test_db):
    db = TestSessionLocal()

    greeting_1 = Greeting(message="Hello, Friend!", type="birthday-bestfriend-messages")
    greeting_2 = Greeting(message="Happy Birthday, Partner!", type="birthday_wife_message")
    greeting_3 = Greeting(message="Hello, Friend! Uno I love you right!", type="birthday-bestfriend-messages")

    db.add(greeting_1)
    db.add(greeting_2)
    db.add(greeting_3)
    db.commit()
    db.close()

    response = client.get('/v1/greetings/?type=Birthday_Bestfriend&limit=10&offset=0')

    assert response.status_code == 200

    greetings = response.json()

    for greeting in greetings:
        assert greeting['type'] == 'birthday-bestfriend-messages'

    assert len(greetings) == 2


def test_limit_get_greetings(test_db):
    db = TestSessionLocal()

    greetings = [
        Greeting(message=f"Message {i}", type="birthday-bestfriend-messages") for i in range(3)
    ]

    db.bulk_save_objects(greetings)
    db.commit()
    db.close()

    response = client.get('/v1/greetings/?type=Birthday_Bestfriend&limit=2')
    greetings = response.json()

    assert response.status_code == 200
    assert len(greetings) == 2


def test_offset_get_greetings(test_db):
    db = TestSessionLocal()

    greetings = [
        Greeting(message=f"Message {i}", type="birthday-to-brother-messages") for i in range(5)
    ]

    db.bulk_save_objects(greetings)
    db.commit()
    db.close()

    response = client.get('v1/greetings/?type=Birthday_Brother&limit=2&offset=2')
    all_greetings = response.json()

    assert response.status_code == 200
    assert len(all_greetings) == 2
    assert all_greetings[0]['message'] == "Message 2"
    assert all_greetings[1]['message'] == "Message 3"
