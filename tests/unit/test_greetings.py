import pytest
from app.models.greeting import Greeting
from app.database.connection import Base
from tests.unit.test_config import TestSessionLocal, engine, client


# fixture used in setting up and tearing down of the database
@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Utility function to add a given number of greetings to the database for a given test.
def add_greetings_to_db(greeting_type, count, db_session):
    greetings = [
        Greeting(message=f"Message {i}", type=greeting_type) for i in range(count)
    ]
    db_session.bulk_save_objects(greetings)
    db_session.commit()


def test_get_greetings_sucess(test_db):
    db = TestSessionLocal()
    add_greetings_to_db('birthday_boyfriend_message', 1, db)
    db.close()

    response = client.get('/v1/greetings/?type=Birthday_Boyfriend')
    greeting = response.json()[0]

    assert response.status_code == 200
    assert greeting['message'] == "Message 0"


def test_filter_greetings_by_type(test_db):
    db = TestSessionLocal()

    add_greetings_to_db("birthday-bestfriend-messages", 3, db)
    db.close()

    response = client.get('/v1/greetings/?type=Birthday_Bestfriend&limit=10&offset=0')

    assert response.status_code == 200

    greetings = response.json()

    for greeting in greetings:
        assert greeting['type'] == 'birthday-bestfriend-messages'

    assert len(greetings) == 3


def test_limit_get_greetings(test_db):
    db = TestSessionLocal()

    add_greetings_to_db("birthday-bestfriend-messages", 3, db)
    db.close()

    response = client.get('/v1/greetings/?type=Birthday_Bestfriend&limit=2')
    greetings = response.json()

    assert response.status_code == 200
    assert len(greetings) == 2


def test_offset_get_greetings(test_db):
    db = TestSessionLocal()

    add_greetings_to_db("birthday-to-brother-messages", 5, db)
    db.close()

    response = client.get('v1/greetings/?type=Birthday_Brother&limit=2&offset=2')
    all_greetings = response.json()

    assert response.status_code == 200
    assert len(all_greetings) == 2
    assert all_greetings[0]['message'] == "Message 2"
    assert all_greetings[1]['message'] == "Message 3"


def test_retrieval_limit_get_greetings(test_db):
    db = TestSessionLocal()

    add_greetings_to_db("birthday-to-brother-messages", 100, db)
    db.close()

    response = client.get("/v1/greetings/?type=Birthday_Brother&limit=100&offset=0")
    all_greetings = response.json()

    assert response.status_code == 200
    assert len(all_greetings) == 100


def test_invalid_type_parameters_get_greetings(test_db):
    invalid_type = "Happy"
    response = client.get(f'/v1/greetings/?type={invalid_type}')

    assert response.status_code == 404
    assert "invalid entry type" in response.json()['detail']


def test_offset_limit_parameter_get_greetings(test_db):
    db = TestSessionLocal()

    add_greetings_to_db("birthday-to-brother-messages", 5, db)
    db.close()

    invalid_offset = 20
    invalid_limit = 20

    response = client.get(f'/v1/greetings/?type=Birthday_Brother&limit={invalid_limit}&offset={invalid_offset}')

    assert response.status_code == 404
    assert "You requested page " in response.json()['detail']


def test_rate_limiter_get_greetings(test_db):
    db = TestSessionLocal()

    add_greetings_to_db("morning-romantic", 1, db)
    db.close()

    response = None

    for _ in range(6):
        response = client.get('/v1/greetings/?type=Morning_Romantic')
        if response.status_code == 429:
            break

    assert response.status_code == 429


def test_limit_retrievel_over_100(test_db):
    db = TestSessionLocal()

    add_greetings_to_db("birthday-to-brother-messages", 5, db)
    db.close()

    exceeded_limit = 101
    response = client.get(f'/v1/greetings/?type=Birthday_Brother&limit={exceeded_limit}&offset=0')

    assert response.status_code == 422
    assert "less than or equal to 100" in response.json()['detail'][0]['msg']


def test_negative_offset_value(test_db):
    db = TestSessionLocal()

    add_greetings_to_db("birthday-to-brother-messages", 1, db)
    db.close()

    negative_offset_value = -1
    response = client.get(f"/v1/greetings/?type=Birthday_Brother&limit=10&offset={negative_offset_value}")
    assert response.status_code == 400
    assert "cannot be negative" in response.json()['detail']
