from tests.unit.test_config import TestSessionLocal, client, add_greetings_to_db, test_db
from app.models.greeting import Greeting
from datetime import datetime


# This test checks that a random message is selected and returned successfully
def test_get_recent_greetings(test_db):
    date = datetime.now().isoformat()
    db = TestSessionLocal()
    db.add(Greeting(message="Hello", type="morning-romantic", created_at=str(date)))
    db.commit()
    db.close()

    request = client.get('/v1/greetings/recent_greetings')
    response = request.json()
    keys = {"message", "type", "created_at"}
    created_at = datetime.fromisoformat(response[0]['created_at'])
    current_year = datetime.today().year
    current_month = datetime.today().month

    assert request.status_code == 200
    assert len(response) == 1
    for key in response[0].keys():
        assert key in keys
    assert current_year == created_at.year
    assert current_month == created_at.month


def test_no_recent_greetings(test_db):

    request = client.get("/v1/greetings/recent_greetings")
    response = request.json()

    assert request.status_code == 404
    assert 'No new greetings have been added' in response['detail']

# TODO test different times in the month -- aka mock datatime
# TODO tests for large volume of data retrieval
# TODO test these EDGE CASES - . Edge Case Tests
# Consider testing edge cases like:
#
# The turn of the year (December to January).
# Leap years (if relevant to your application).
#TODO add test for database failure
# Tests for concurrency