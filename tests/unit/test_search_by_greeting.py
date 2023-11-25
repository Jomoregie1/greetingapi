from tests.unit.conftest import TestSessionLocal, engine, client, add_greetings_to_db, test_db
from app.models.greeting import Greeting


def test_get_greeting_by_search_with_query(test_db):
    db = TestSessionLocal()
    add_greetings_to_db("birthday_boyfriend_message", 2, db)
    db.close()

    search_phrase = "Message"

    request = client.get(f'/v1/greetings/search?query={search_phrase}')
    responses = request.json()

    assert request.status_code == 200
    assert 'Message' in responses[0]['message']


def test_search_for_non_existant_message(test_db):
    db = TestSessionLocal()

    add_greetings_to_db('birthday_love_message', 3, db)
    db.close()

    search_term = "Non_existent_term"
    request = client.get(f'/v1/greetings/search?query={search_term}')
    response = request.json()

    assert request.status_code == 404
    assert "No greetings found" in response['detail']


def test_search_for_type_and_phrase(test_db):
    db = TestSessionLocal()
    add_greetings_to_db("birthday-to-dad-messages", 5, db)
    db.close()

    request = client.get(f'v1/greetings/search?type=Birthday_Dad&query=Message')

    assert request.status_code == 200
    assert len(request.json()) == 5
    assert "birthday-to-dad" in request.json()[0]['type']


def test_no_existant_type():
    request = client.get(f'v1/greetings/search?type=hello&query=Message')

    assert request.status_code == 404
    assert "does not exist" in request.json()['detail']


def test_type_exist_no_returns(test_db):
    db = TestSessionLocal()
    db.add(Greeting(type="birthday-to-dad-messages"))
    db.commit()
    db.close()
    search_term = "non-existence"
    request = client.get(f'/v1/greetings/search?type=Birthday_Dad&query={search_term}')
    response = request.json()

    assert request.status_code == 404
    assert 'No greetings found' in response['detail']


def test_search_no_query_specified():

    request = client.get(f'/v1/greetings/search')
    response = request.json()

    assert request.status_code == 422
    assert 'missing' in response['detail'][0]['type']


