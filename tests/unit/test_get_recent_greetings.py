import pytest
import asyncio
from tests.unit.conftest import async_client_with_rate_limiter, async_client_no_rate_limit, add_greetings_to_db, \
    test_db, get_greetings
from app.models.greeting import Greeting
from datetime import datetime, timedelta
from freezegun import freeze_time

def generate_greetings(greeting_type, date, count):
    return [Greeting(message=f"Test Message {i}", type=greeting_type, created_at=date) for i in range(count)]


# This test checks that a random message is selected and returned successfully
@pytest.mark.asyncio
async def test_get_recent_greetings(test_db, async_client_no_rate_limit):
    date = datetime.now().isoformat()
    greeting = generate_greetings("morning-romantic", date, 1)
    await add_greetings_to_db(greeting)

    request = await async_client_no_rate_limit.get('/v1/greetings/recent_greetings')
    response = request.json()
    created_at = datetime.fromisoformat(response['greetings'][0]['created_at'])
    current_year = datetime.today().year
    current_month = datetime.today().month

    assert request.status_code == 200
    assert len(response['greetings']) == 1
    assert current_year == created_at.year
    assert current_month == created_at.month


@pytest.mark.asyncio
async def test_no_recent_greetings(test_db, async_client_no_rate_limit):
    request = await async_client_no_rate_limit.get("/v1/greetings/recent_greetings")
    response = request.json()

    assert request.status_code == 404
    assert 'No new greetings have been added' in response['detail']


@pytest.mark.asyncio
@freeze_time("2020-02-29")
async def test_get_greetings_different_dates(test_db, async_client_no_rate_limit):
    date = datetime.now().isoformat()
    day_after_date = (datetime.now() + timedelta(days=1)).isoformat()

    greeting_today = generate_greetings("morning-romantic", date, 1)
    greeting_next_day = generate_greetings("birthday-to-dad-messages", day_after_date, 1)

    await add_greetings_to_db(greeting_today)
    await add_greetings_to_db(greeting_next_day)

    # Testing for new month
    with freeze_time("2020-03-01"):
        request = await async_client_no_rate_limit.get("/v1/greetings/recent_greetings")
        response = request.json()
        assert request.status_code == 200
        assert len(response['greetings']) == 1
        assert "2020-03-01" in response['greetings'][0]['created_at']

    # Testing for previous month
    request = await async_client_no_rate_limit.get("/v1/greetings/recent_greetings")
    response = request.json()

    assert request.status_code == 200
    assert len(response['greetings']) == 1
    assert "2020-02-29" in response['greetings'][0]['created_at']


@pytest.mark.asyncio
async def test_greeting_type(test_db, async_client_no_rate_limit):
    current_date = datetime.now().isoformat()

    greeting = generate_greetings('christmas-messages', current_date, 1)
    await add_greetings_to_db(greeting)

    request = await async_client_no_rate_limit.get("/v1/greetings/recent_greetings?category=Christmas_General")
    response = request.json()

    assert request.status_code == 200
    assert len(response['greetings']) == 1
    assert "christmas-messages" in response['greetings'][0]["type"]


@pytest.mark.asyncio
async def test_incorrect_greeting_type(test_db, async_client_no_rate_limit):
    current_date = datetime.now().isoformat()
    greeting = generate_greetings('christmas-messages', current_date, 1)
    await add_greetings_to_db(greeting)

    request = await async_client_no_rate_limit.get("/v1/greetings/recent_greetings?category=messages")
    response = request.json()

    assert request.status_code == 404
    assert "invalid entry type" in response["detail"]


@pytest.mark.asyncio
async def test_limit_of_greetings_type(test_db, async_client_no_rate_limit):
    date = datetime.now().isoformat()
    number_of_messages = 100

    greetings = generate_greetings('morning-romantic', date, number_of_messages)
    await add_greetings_to_db(greetings)

    max_limit = 100
    request = await async_client_no_rate_limit.get(
        f"/v1/greetings/recent_greetings?category=Morning_Romantic&limit={max_limit}")
    response = request.json()

    assert request.status_code == 200
    assert len(response['greetings']) == 100


@pytest.mark.asyncio
async def test_limit_of_greetings_exceeded(test_db, async_client_no_rate_limit):
    date = datetime.now().isoformat()

    greeting = generate_greetings('morning-romantic', date, 1)
    await add_greetings_to_db(greeting)

    exceeding_max_value = 101

    request = await async_client_no_rate_limit.get(f"/v1/greetings/recent_greetings?limit={exceeding_max_value}")
    response = request.json()

    assert request.status_code == 422
    assert "Input should be less than or equal to 100" in response['detail'][0]['msg']


@pytest.mark.asyncio
async def test_negative_offset(test_db, async_client_no_rate_limit):
    date = datetime.now().isoformat()

    number_of_greetings = 100
    greetings = generate_greetings('morning-romantic', date, number_of_greetings)
    await add_greetings_to_db(greetings)

    request = await  async_client_no_rate_limit.get("/v1/greetings/recent_greetings?offset=-1")
    response = request.json()

    assert request.status_code == 422
    assert "Input should be greater than or equal to 0" in response["detail"][0]['msg']


@pytest.mark.asyncio
async def test_pagination_functionality(test_db, async_client_no_rate_limit):
    date = datetime.now().isoformat()

    number_of_greetings = 200
    greetings = generate_greetings('morning-romantic', date, number_of_greetings)
    await add_greetings_to_db(greetings)

    request = await async_client_no_rate_limit.get("/v1/greetings/recent_greetings?limit=10")
    response = request.json()

    assert request.status_code == 200
    assert response["total_pages"] == 20


@pytest.mark.asyncio
async def test_offset_equal_to_number_of_greetings(test_db, async_client_no_rate_limit):

    date = datetime.now().isoformat()

    number_of_greetings = 200
    greetings = generate_greetings('morning-romantic',date,number_of_greetings)
    await add_greetings_to_db(greetings)

    request = await async_client_no_rate_limit.get("/v1/greetings/recent_greetings?offset=200")
    response = request.json()

    assert request.status_code == 404
    assert "exceeds the total available pages" in response["detail"]

@pytest.mark.asyncio
async def test_zero_limit_value(test_db,async_client_no_rate_limit):

    request = await async_client_no_rate_limit.get("v1/greetings/recent_greetings?limit=0&offset=0")
    response = request.json()

    assert request.status_code == 422
    assert "Input should be greater than or equal to 1" in response["detail"][0]['msg']

# TODO ensure filters work together effectively. (Functional tests)
# TODO ensure proper error handling is there for database connection issues.
# TODO add documentation to tests.
