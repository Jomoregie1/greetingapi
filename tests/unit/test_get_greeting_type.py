from app.models.greeting import Greeting
from tests.unit.conftest import TestSessionLocal, client, test_db


# Test for happy path, returns the correct status code and the correct data.
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


# Test for no types avaliable

def test_no_greeting_type_result(test_db):
    db = TestSessionLocal()

    greeting = Greeting(message="default message")
    db.add(greeting)
    db.commit()
    db.close()

    response = client.get('/v1/greetings/types')

    assert response.status_code == 404
    assert 'No types' in response.json()['detail']
