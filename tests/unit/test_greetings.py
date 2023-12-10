import time
import pytest
from tests.unit.conftest import async_client_with_rate_limiter, test_db, get_greetings, add_greetings_to_db, \
    async_client_no_rate_limit
import asyncio


@pytest.mark.asyncio
async def test_get_greetings_success(test_db, async_client_no_rate_limit):
    greeting = get_greetings('birthday_boyfriend_message', 1)
    await add_greetings_to_db(greeting)

    request = await async_client_no_rate_limit.get('/v1/greetings/?type=Birthday_Boyfriend')

    response = request.json()
    print(response)
    assert request.status_code == 200
    assert "Test Message" in response['greetings'][0]['message']


@pytest.mark.asyncio
async def test_filter_greetings_by_type(test_db, async_client_no_rate_limit):
    greetings = get_greetings("birthday-bestfriend-messages", 3)
    await add_greetings_to_db(greetings)

    request = await async_client_no_rate_limit.get('/v1/greetings/?type=Birthday_Bestfriend&limit=10&offset=0')
    response = request.json()

    assert request.status_code == 200
    for greeting in response["greetings"]:
        assert greeting['type'] == 'birthday-bestfriend-messages'
    assert len(greetings) == 3


@pytest.mark.asyncio
async def test_limit_get_greetings(test_db, async_client_no_rate_limit):
    greetings = get_greetings("birthday-bestfriend-messages", 3)
    await add_greetings_to_db(greetings)

    request = await async_client_no_rate_limit.get('/v1/greetings/?type=Birthday_Bestfriend&limit=2')
    response = request.json()

    assert request.status_code == 200
    assert len(response["greetings"]) == 2


@pytest.mark.asyncio
async def test_offset_get_greetings(test_db, async_client_no_rate_limit):
    greetings = get_greetings("birthday-to-brother-messages", 5)
    await add_greetings_to_db(greetings)

    request = await async_client_no_rate_limit.get('v1/greetings/?type=Birthday_Brother&limit=2&offset=2')
    response = request.json()

    assert request.status_code == 200
    assert len(response["greetings"]) == 2
    assert response["greetings"][0]['message'] == "Test Message 2"
    assert response["greetings"][1]['message'] == "Test Message 3"


@pytest.mark.asyncio
async def test_retrieval_limit_get_greetings(test_db, async_client_no_rate_limit):
    greetings = get_greetings("birthday-to-brother-messages", 100)
    await add_greetings_to_db(greetings)

    request = await async_client_no_rate_limit.get("/v1/greetings/?type=Birthday_Brother&limit=100&offset=0")
    response = request.json()

    assert request.status_code == 200
    assert len(response["greetings"]) == 100


@pytest.mark.asyncio
async def test_invalid_type_parameters_get_greetings(test_db, async_client_no_rate_limit):
    invalid_type = "Happy"

    request = await async_client_no_rate_limit.get(f'/v1/greetings/?type={invalid_type}')
    response = request.json()

    assert request.status_code == 404
    assert "invalid entry type" in response['detail']


@pytest.mark.asyncio
async def test_offset_limit_parameter_get_greetings(test_db, async_client_no_rate_limit):
    greetings = get_greetings("birthday-to-brother-messages", 5)
    await add_greetings_to_db(greetings)

    invalid_offset = 20
    invalid_limit = 20

    request = await async_client_no_rate_limit.get(
        f'/v1/greetings/?type=Birthday_Brother&limit={invalid_limit}&offset={invalid_offset}')

    assert request.status_code == 404
    assert "You requested page " in request.json()['detail']


@pytest.mark.asyncio
async def test_rate_limiter_get_greetings(test_db, async_client_with_rate_limiter):
    greeting = get_greetings("morning-romantic", 1)
    await add_greetings_to_db(greeting)

    response = None

    for _ in range(6):
        response = await async_client_with_rate_limiter.get('/v1/greetings/?type=Morning_Romantic')
        if response.status_code == 429:
            break

    assert response.status_code == 429


@pytest.mark.asyncio
async def test_limit_retrievel_over_100(test_db, async_client_no_rate_limit):
    greetings = get_greetings("birthday-to-brother-messages", 5)
    await add_greetings_to_db(greetings)

    exceeded_limit = 101
    request = await async_client_no_rate_limit.get(
        f'/v1/greetings/?type=Birthday_Brother&limit={exceeded_limit}&offset=0')

    assert request.status_code == 422
    assert "less than or equal to 100" in request.json()['detail'][0]['msg']


@pytest.mark.asyncio
async def test_negative_offset_value(test_db, async_client_no_rate_limit):
    greeting = get_greetings("birthday-to-brother-messages", 1)
    await add_greetings_to_db(greeting)

    negative_offset_value = -1

    request = await async_client_no_rate_limit.get(
        f"/v1/greetings/?type=Birthday_Brother&limit=10&offset={negative_offset_value}")
    response = request.json()

    assert request.status_code == 422
    assert "greater than or equal to 0" in response['detail'][0]['msg']


@pytest.mark.asyncio
async def test_pagination_functionality(test_db, async_client_no_rate_limit):
    greeting = get_greetings("birthday-to-brother-messages", 200)
    await add_greetings_to_db(greeting)

    request = await async_client_no_rate_limit.get("/v1/greetings/?type=Birthday_Brother&limit=100")
    response = request.json()

    assert request.status_code == 200
    assert response['total_pages'] == 2


@pytest.mark.asyncio
async def test_cache_behavior(test_db, async_client_with_rate_limiter):
    greetings = get_greetings("birthday-to-brother-messages", 10)
    await add_greetings_to_db(greetings)

    start = time.perf_counter()
    first_response = await async_client_with_rate_limiter.get('/v1/greetings/?type=Birthday_Brother')
    first_time = time.perf_counter() - start

    start = time.perf_counter()
    second_response = await async_client_with_rate_limiter.get('/v1/greetings/?type=Birthday_Brother')
    second_time = time.perf_counter() - start

    assert second_response.json() == first_response.json()
    assert second_time < first_time


@pytest.mark.asyncio
async def test_concurrent_request(test_db, async_client_no_rate_limit):
    endpoint = "/v1/greetings/?type=Birthday_Brother"
    request_count = 20
    greetings = get_greetings("birthday-to-brother-messages", 10)
    await add_greetings_to_db(greetings)

    tasks = [async_client_no_rate_limit.get(endpoint) for _ in range(request_count)]
    responses = await asyncio.gather(*tasks)

    for requests in responses:
        response = requests.json()

        assert requests.status_code == 200
        assert "Test" in response["greetings"][0]['message']
