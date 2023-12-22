import pytest
import asyncio
from tests.unit.conftest import add_greetings_to_db, test_db, async_client_with_rate_limiter, \
    async_client_no_rate_limit, get_greetings
from app.models.greeting import Greeting


@pytest.mark.asyncio
async def test_get_greeting_by_search_with_query(test_db, async_client_no_rate_limit):
    greetings = get_greetings("birthday_boyfriend_message", 2)
    await add_greetings_to_db(greetings)

    search_phrase = "Message"

    request = await async_client_no_rate_limit.get(f'/v1/greetings/search?query={search_phrase}')
    responses = request.json()

    assert request.status_code == 200
    assert 'Message' in responses['greetings'][0]['message']


@pytest.mark.asyncio
async def test_search_for_non_existant_message(test_db, async_client_no_rate_limit):
    greetings = get_greetings('birthday_love_message', 3)
    await add_greetings_to_db(greetings)

    search_term = "Non_existent_term"
    request = await async_client_no_rate_limit.get(f'/v1/greetings/search?query={search_term}')
    response = request.json()

    assert request.status_code == 404
    assert "No greetings found" in response['detail']


@pytest.mark.asyncio
async def test_search_for_type_and_phrase(test_db, async_client_no_rate_limit):
    greetings = get_greetings("birthday-to-dad-messages", 5)
    await add_greetings_to_db(greetings)

    request = await async_client_no_rate_limit.get(f'v1/greetings/search?category=Birthday_Dad&query=Message')
    response = request.json()

    assert request.status_code == 200
    assert len(response["greetings"]) == 5
    assert "birthday-to-dad" in response["greetings"][0]['type']


@pytest.mark.asyncio
async def test_no_existant_type(async_client_no_rate_limit):
    request = await async_client_no_rate_limit.get(f'v1/greetings/search?category=hello&query=Message')
    response = request.json()

    assert request.status_code == 404
    assert "invalid entry type" in response['detail']

@pytest.mark.asyncio
async def test_search_no_query_specified(async_client_no_rate_limit):
    request = await async_client_no_rate_limit.get(f'/v1/greetings/search')
    response = request.json()

    assert request.status_code == 422
    assert 'missing' in response['detail'][0]['type']
