import pytest
import asyncio
from app.models.greeting import Greeting
from tests.unit.conftest import async_client_with_rate_limiter, test_db, get_greetings, add_greetings_to_db


# Test for happy path, returns the correct status code and the correct data.
@pytest.mark.asyncio
async def test_get_types(test_db,async_client_with_rate_limiter):
    types = ["morning-romantic", "birthday-to-mom-messages", "birthday-to-brother-messages"]
    greetings = [get_greetings(type, 1) for type in types]
    await asyncio.gather(*(add_greetings_to_db(greeting) for greeting in greetings))

    request = await async_client_with_rate_limiter.get('v1/greetings/types')
    response = request.json()

    expected_list = ['Birthday_Brother', 'Birthday_Mom', 'Morning_Romantic']

    assert request.status_code == 200
    assert response['types'] == expected_list


# Test for no types avaliable
@pytest.mark.asyncio
async def test_no_greeting_type_result(test_db, async_client_with_rate_limiter):

    request = await async_client_with_rate_limiter.get('/v1/greetings/types')
    response = request.json()

    assert request.status_code == 404
    assert 'No types' in response['detail']



