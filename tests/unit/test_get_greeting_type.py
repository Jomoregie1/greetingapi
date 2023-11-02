import logging
import pytest
from app.models.greeting import Greeting
from app.database.connection import Base
from tests.unit.test_config import TestSessionLocal, engine, client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.INFO)


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_get_types(test_db):
    db = TestSessionLocal()

    types = ["morning-romantic", "birthday-to-mom-messages", "birthday-to-brother-messages"]

    greetings = [
        Greeting(message="default message", type=type) for type in types
    ]

    db.bulk_save_objects(greetings)
    db.commit()
    db.close()

    response = client.get('v1/greetings/types')
    expected_list = ['Birthday_Brother', 'Birthday_Mom', 'Morning_Romantic']

    assert response.status_code == 200
    assert response.json() == expected_list


def test_no_greeting_type_result(test_db):
    db = TestSessionLocal()

    greeting = Greeting(message="default message")
    db.add(greeting)
    db.commit()
    db.close()

    response = client.get('/v1/greetings/types')

    assert response.status_code == 404
    assert 'No types' in response.json()['detail']
