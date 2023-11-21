from tests.unit.test_config import TestSessionLocal, client, add_greetings_to_db, test_db
from app.models.greeting import Greeting
from datetime import datetime, timedelta
from freezegun import freeze_time


def add_multiple_greetings(created_at, num_of_messages, db, type):
    greetings = [Greeting(message=f"Test message {i}",
                          created_at=created_at, type=type) for i in range(num_of_messages)]
    db.bulk_save_objects(greetings)
    db.commit()


# This test checks that a random message is selected and returned successfully
def test_get_recent_greetings(test_db):
    date = datetime.now().isoformat()
    db = TestSessionLocal()
    db.add(Greeting(message="Hello", type="morning-romantic", created_at=str(date)))
    db.commit()
    db.close()

    request = client.get('/v1/greetings/recent_greetings')
    response = request.json()
    created_at = datetime.fromisoformat(response[0]['created_at'])
    current_year = datetime.today().year
    current_month = datetime.today().month

    assert request.status_code == 200
    assert len(response) == 1
    assert current_year == created_at.year
    assert current_month == created_at.month


def test_no_recent_greetings(test_db):
    request = client.get("/v1/greetings/recent_greetings")
    response = request.json()

    assert request.status_code == 404
    assert 'No new greetings have been added' in response['detail']


@freeze_time("2020-02-29")
def test_get_greetings_different_dates(test_db):
    date = datetime.now().isoformat()
    day_after_date = (datetime.now() + timedelta(days=1)).isoformat()
    db = TestSessionLocal()
    db.add(Greeting(message="Hello", type="morning-romantic", created_at=str(date)))
    db.add(Greeting(message="Happy birthday", type="birthday-to-dad-messages", created_at=str(day_after_date)))
    db.commit()
    db.close()

    # Testing for new month
    with freeze_time("2020-03-01"):
        request = client.get("/v1/greetings/recent_greetings")
        response = request.json()
        assert request.status_code == 200
        assert len(response) == 1
        assert "2020-03-01" in response[0]['created_at']

    # Testing for previous month
    request = client.get("/v1/greetings/recent_greetings")
    response = request.json()

    assert request.status_code == 200
    assert len(response) == 1
    assert "2020-02-29" in response[0]['created_at']


def test_greeting_type(test_db):
    db = TestSessionLocal()
    current_date = datetime.now().isoformat()
    db.add(Greeting(message="Test message", type="christmas-messages", created_at=current_date))
    db.commit()
    db.close()

    request = client.get("/v1/greetings/recent_greetings?type=Christmas_General")
    response = request.json()

    assert request.status_code == 200
    assert len(response) == 1
    assert "christmas-messages" in response[0]["type"]


def test_incorrect_greeting_type(test_db):
    db = TestSessionLocal()
    current_date = datetime.now().isoformat()
    db.add(Greeting(message="Test message", type="christmas-messages", created_at=current_date))
    db.commit()
    db.close()

    request = client.get("/v1/greetings/recent_greetings?type=messages")
    assert request.status_code == 404
    assert "type entered does not exist" in request.json()["detail"]


def test_limit_of_greetings_type(test_db):
    db = TestSessionLocal()
    date = datetime.now().isoformat()
    number_of_messages = 105
    add_multiple_greetings(date, number_of_messages, db, type='morning-romantic')
    db.close()

    max_limit = 100
    request = client.get(f"/v1/greetings/recent_greetings?type=Morning_Romantic&limit={max_limit}")
    assert request.status_code == 200
    assert len(request.json()) == 100


def test_limit_of_greetings_exceeded(test_db):
    db = TestSessionLocal()
    date = datetime.now().isoformat()
    db.add(Greeting(message="testmessage", type="morning-romantic", created_at=date))
    db.commit()
    db.close()

    exceeding_max_value = 101
    request = client.get(f"/v1/greetings/recent_greetings?limit={exceeding_max_value}")

    assert request.status_code == 422
    assert "Input should be less than or equal to 100" in request.json()['detail'][0]['msg']


def test_negative_offset(test_db):
    db = TestSessionLocal()
    date = datetime.now().isoformat()
    add_multiple_greetings(date, 100, db, "morning-romantic")
    db.close()

    request = client.get("/v1/greetings/recent_greetings?offset=-1")
    assert request.status_code == 422
    print(request.json())
    assert "Input should be greater than or equal to 0" in request.json()["detail"][0]['msg']


def test_pagination_functionality(test_db):
    db = TestSessionLocal()
    date = datetime.now().isoformat()
    add_multiple_greetings(date, 200, db, "morning-romantic")
    db.close()

    request = client.get("/v1/greetings/recent_greetings?limit=10")
    response = request.json()

    assert request.status_code == 200
    assert response[0]["total_pages"] == 20


def test_offset_equal_to_number_of_greetings(test_db):
    db = TestSessionLocal()
    date = datetime.now().isoformat()
    add_multiple_greetings(date, 200, db, "morning-romantic")
    db.close()

    request = client.get("/v1/greetings/recent_greetings?offset=200")
    response = request.json()

    assert request.status_code == 404
    assert "exceeds the total available pages" in response["detail"]


def test_zero_limit_value(test_db):

    request = client.get("v1/greetings/recent_greetings?limit=0&offset=0")
    assert request.status_code == 422
    assert "Input should be greater than or equal to 1" in request.json()["detail"][0]['msg']


# TODO ensure filters work together effectively. (Functional tests)
# TODO ensure proper error handling is there for database connection issues.
# TODO add documentation to tests.

