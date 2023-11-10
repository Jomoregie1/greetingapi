from tests.unit.test_config import TestSessionLocal, client, add_greetings_to_db,test_db


# This test checks that a random message is selected and returned sucessfully
def test_get_random_greeting(test_db):
    db = TestSessionLocal()
    add_greetings_to_db('morning-romantic', 4, db)
    db.close()

    pos_msg_choices = {'Message 0', 'Message 1', 'Message 2', 'Message 3'}
    response = client.get('/v1/greetings/random?type=Morning_Romantic')

    assert response.status_code == 200
    assert response.json()['message'] in pos_msg_choices


# This test checks if there are no messages for a given type
def test_no_message_for_given_type(test_db):
    db = TestSessionLocal()
    add_greetings_to_db('birthday-bestfriend-messages', 10, db)
    db.close()

    response = client.get('/v1/greetings/random?type=Birthday_Dad')
    assert response.status_code == 404
    assert 'not found' in response.json()['detail']


# This test for an invalid type parameter
def test_get_random_greeting_invalid_type(test_db):
    response = client.get('/v1/greetings/random?type=Invalid_Type')
    assert response.status_code == 400
    assert 'Invalid' in response.json()['detail']


# This test checks if a 422 status code is provided if no type is present in params
def test_no_greeting_type_provided(test_db):
    response = client.get('/v1/greetings/random')
    assert response.status_code == 422
    assert response.json()['detail'][0]['type'] == 'missing'
