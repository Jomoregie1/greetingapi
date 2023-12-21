import pytest
import asyncio
from tests.unit.conftest import add_greetings_to_db, test_db, get_greetings, async_client_no_rate_limit, \
    async_client_with_rate_limiter


# This test checks that a random message is selected and returned sucessfully
@pytest.mark.asyncio
async def test_get_random_greeting(test_db, async_client_no_rate_limit):
    greetings = get_greetings("morning-romantic", 4)
    await add_greetings_to_db(greetings)

    pos_msg_choices = {'Test Message 0', 'Test Message 1', 'Test Message 2', 'Test Message 3'}
    request = await async_client_no_rate_limit.get('/v1/greetings/random?type=Morning_Romantic')
    response = request.json()

    assert request.status_code == 200
    assert response['greeting'][0]['message'] in pos_msg_choices
    assert response['greeting'][0]['type'] == "Morning_Romantic"


# This test checks if there are no messages for a given type
@pytest.mark.asyncio
async def test_no_message_for_given_type(test_db, async_client_no_rate_limit):
    greeting = get_greetings('birthday-bestfriend-messages', 10)
    await add_greetings_to_db(greeting)

    request = await async_client_no_rate_limit.get('/v1/greetings/random?type=Birthday_Dad')
    response = request.json()
    assert request.status_code == 404
    assert 'No greetings found' in response['detail']


# This test for an invalid type parameter
@pytest.mark.asyncio
async def test_get_random_greeting_invalid_type(test_db, async_client_no_rate_limit):
    request = await async_client_no_rate_limit.get('/v1/greetings/random?type=Invalid_Type')
    response = request.json()
    print(response)

    assert request.status_code == 404
    assert 'invalid' in response['detail']


# This test checks if a 422 status code is provided if no type is present in params
@pytest.mark.asyncio
async def test_no_greeting_type_provided(test_db, async_client_no_rate_limit):
    request = await async_client_no_rate_limit.get('/v1/greetings/random')
    response = request.json()

    assert request.status_code == 422
    assert response['detail'][0]['type'] == 'missing'
