import random
from datetime import datetime
from typing import Optional, Tuple, AsyncGenerator, List, Any, Sequence
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi import Request
from fastapi_cache.decorator import cache
from sqlalchemy import text, extract, select, func, Row, RowMapping
from sqlalchemy.engine.result import _TP
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import AsyncSessionLocal
from app.models.greeting import Greeting
from app.routers.greeting_types import GreetingType
from app.schemas.greeting_schema import GreetingResponseModel, GreetingResponse, TypeResponse
from app.routers.config import EXPIRATION_TIME

router = APIRouter()


# TODO continue to refactor code, where doc strings are added and abstracting some functionality from the endpoint
#  functions would be helpful.
async def get_db() -> AsyncGenerator[AsyncSessionLocal, None]:
    """
        Create and provide a database session.

        This asynchronous function creates a session using AsyncSessionLocal. It yields
        the session for use in other parts of the application.

        Yields:
            session: An instance of the database session, created using AsyncSessionLocal.

        Usage:
            async for session in get_db():
                # Use session for database operations.
        """
    async with AsyncSessionLocal() as session:
        yield session


def validate_type(greeting_type: str) -> GreetingType:
    """
    Used to validate the given greeting type value.

    Args:
        greeting_type(str):  a string representing the greeting type.

    Returns:
        GreetingType: The validated greeting type value corresponding to the GreetingType enum.

    Raises:
        HTTPExecption: if the provided greeting_type is not a valid GreetingType entity.

    """
    try:
        greeting_value = GreetingType[greeting_type].value
    except KeyError:
        raise HTTPException(status_code=404, detail="This is an invalid entry type")
    return greeting_value


def calculateGreetingPagination(total_greetings: int, limit: int, offset: int) -> Tuple[int, int, int]:
    """
    Calculates the total_pages, offset_limit and current page used for pagnation.

    Args:
        total_greetings(int): total greetings for a given query.
        limit(int): the current limit being applied to a query.
        offset(int): the current offset value being applied to a query.

    Returns:
        total_pages(int): This is the total pages avaliable for a given request.
        offset_limit(int): This is the max value for the offset that can be given during a given request.
        current_page(int): The current page, for a given request.
    """
    total_pages = (total_greetings + limit - 1) // limit
    offset_limit = 0 if total_pages == 0 else (total_pages * limit) - limit
    current_page = offset // limit + 1

    return total_pages, offset_limit, current_page


async def count_greetings_by_type(db: AsyncSession, validated_greeting_type: GreetingType) -> int:
    """
        Count the number of greetings of a specific type.

        Args:
            db (AsyncSession): The database session.
            validated_greeting_type(GreetingType): The type of greeting to count.

        Returns:
            int: The total count of greetings for specified type.
        """
    total_greetings_query = select(func.count()).select_from(Greeting).filter(Greeting.type == validated_greeting_type)
    total_greetings_result = await db.execute(total_greetings_query)
    total_greetings = total_greetings_result.scalar_one()
    return total_greetings


async def count_greetings_with_conditions(db: AsyncSession, conditions: List, query: Optional[str] = None) -> int:
    """
    Count the number of greetings based on specified conditions, with an optional query.

    Args:
        db (AsyncSession): The database session.
        conditions (List): A list of SQLAlchemy conditions to filter the query.
        query (Optional[str]): An optional query parameter to be used in the query.

    Returns:
        int: The count of greetings that meet the specified conditions and optional query.
    """
    total_greetings_query = select(func.count(Greeting.message)).select_from(Greeting).filter(*conditions)

    if query:
        total_greetings_query = total_greetings_query.params(query=query)

    total_greetings_result = await db.execute(total_greetings_query)
    total_greetings = total_greetings_result.scalar_one()
    return total_greetings


async def fetch_greetings(db: AsyncSession, query: Select, fetch_scalar: Optional[bool] = False) -> Sequence[Row[_TP]] | \
                                                                                                    Sequence[
                                                                                                        Row | RowMapping | Any]:
    """
    Retrieves,greetings from the database

    Args:
        db(AsyncSession): The database session
        query(Select): The query to be executed
        fetch_scalar(bool): flag used to fetch scalars values.

    Returns:
        greetings: returns a list of greetings.
    """
    greetings = await db.execute(query)

    if fetch_scalar:
        greetings = greetings.all()
    else:
        greetings = greetings.scalars().all()

    return greetings


@router.get("/", response_model=GreetingResponseModel)
@cache(expire=EXPIRATION_TIME)
async def get_greetings(request: Request,
                        category: str = Query(..., description="Type of greeting", enum=list(GreetingType.__members__)),
                        limit: int = Query(10, description="Limit the number of greetings returned", ge=1, le=100),
                        offset: int = Query(0, description="The starting point from which to retrieve the set of "
                                                           "records.", ge=0),
                        db: AsyncSession = Depends(get_db)):
    validated_greeting_type = validate_type(category)
    query = select(Greeting).filter(Greeting.type == validated_greeting_type).offset(offset).limit(limit)

    try:
        greetings = await fetch_greetings(db, query)
        total_greetings = await count_greetings_by_type(db, validated_greeting_type)

    except (OperationalError, SQLAlchemyError):
        raise HTTPException(status_code=500, detail='Internal Server Error')

    total_pages, offset_limit, current_page = calculateGreetingPagination(total_greetings, limit, offset)

    if offset > offset_limit:
        raise HTTPException(status_code=404,
                            detail=f"You requested page {offset // limit + 1} which exceeds the total available "
                                   f"pages ({total_pages}). Please request a page number between"
                                   f" 1 and {total_pages}.")

    response = GreetingResponseModel(total_greetings=total_greetings,
                                     total_pages=total_pages,
                                     current_page=current_page,
                                     greetings=[{"message": greeting.message,
                                                 "type": greeting.type} for greeting in greetings])

    return response


@router.get('/random', response_model=GreetingResponse)
async def get_random_greeting(request: Request
                              , category: str = Query(..., description="Type of greeting",
                                                      enum=list(GreetingType.__members__))
                              , db: AsyncSession = Depends(get_db)):
    greeting_type = validate_type(category)
    query = select(Greeting.message).select_from(Greeting).filter(
        Greeting.type == greeting_type)
    try:
        greetings = await fetch_greetings(db, query)

    except (OperationalError, SQLAlchemyError):
        raise HTTPException(status_code=500, detail='Internal Server Error')

    if not greetings:
        raise HTTPException(status_code=404, detail="No greetings found")

    message = random.choice(greetings)

    response = GreetingResponse(greeting=[{
        "message": message,
        "type": category,
    }]).model_dump()

    return response


# An endpoint that simply retrieves all types, and returns all unique user-friendly types to the user.
@router.get('/types', response_model=TypeResponse)
@cache(expire=EXPIRATION_TIME)
async def get_greeting_types(request: Request, db: AsyncSession = Depends(get_db)):
    query = select(Greeting.type).select_from(Greeting).distinct()

    try:
        greeting_types = await fetch_greetings(db, query)

    except (OperationalError, SQLAlchemyError):
        raise HTTPException(status_code=500, detail='Internal Server Error')

    else:
        if not greeting_types or greeting_types == {None}:
            raise HTTPException(status_code=404, detail="No types available")

        response = [name for name, member in GreetingType.__members__.items() if member.value in greeting_types]
        response = TypeResponse(types=response)

        return response


@router.get('/search', response_model=GreetingResponseModel)
@cache(expire=EXPIRATION_TIME)
async def get_greeting_by_search(request: Request,
                                 category: Optional[str] = Query(None, description="Type of greeting",
                                                                 enum=list(GreetingType.__members__)),
                                 query: str = Query(..., description='Search for messages'),
                                 limit: int = Query(10, description='Limit the number of greetings returned', ge=1,
                                                    le=100),
                                 offset: int = Query(0, description='The starting point from which to retrieve the '
                                                                    'set of records.', ge=0),
                                 db: AsyncSession = Depends(get_db)):
    conditions = [text("MATCH (message) AGAINST (:query IN NATURAL LANGUAGE MODE)")]

    if category:
        category = validate_type(category)
        conditions.append(Greeting.type == category)

    db_query = select(Greeting.message, Greeting.type) \
        .select_from(Greeting) \
        .filter(*conditions) \
        .params(query=query) \
        .offset(offset) \
        .limit(limit)

    try:
        greetings = await fetch_greetings(db, db_query, True)
        total_greetings = await count_greetings_with_conditions(db, conditions, query)

    except (OperationalError, SQLAlchemyError):
        raise HTTPException(status_code=500, detail='Internal Server Error')

    result = [Greeting(message=message, type=category) for (message, category) in greetings]
    total_pages, offset_limit, current_page = calculateGreetingPagination(total_greetings, limit, offset)

    if not result:
        raise HTTPException(status_code=404, detail='No greetings found match the search criteria.')

    if offset > offset_limit:
        raise HTTPException(status_code=404,
                            detail=f"You requested page {offset // limit + 1} which exceeds the total available "
                                   f"pages ({total_pages}). Please request a page number between"
                                   f" 1 and {total_pages}.")

    response = GreetingResponseModel(total_greetings=total_greetings,
                                     total_pages=total_pages,
                                     current_page=current_page,
                                     greetings=[{
                                         "message": greeting.message,
                                         "type": greeting.type
                                     } for greeting in result])

    return response


@router.get('/recent_greetings', response_model=GreetingResponseModel)
@cache(expire=EXPIRATION_TIME)
async def get_recent_greetings(request: Request,
                               category: Optional[str] = Query(None, description="Type of greeting",
                                                               enum=list(GreetingType.__members__)),
                               limit: int = Query(10, description="Limit the number of greetings returned", ge=1,
                                                  le=100),
                               offset: int = Query(0,
                                                   description="The starting point from which to retrieve the set of "
                                                               "records. "
                                                               "An offset of 0 will start from the beginning of the "
                                                               "dataset. "
                                                               "Use in conjunction with the 'limit' parameter to "
                                                               "paginate "
                                                               "through records. For example, an offset of 10 with a "
                                                               "limit "
                                                               "of 5 "
                                                               "will retrieve records 11 through 15.", ge=0),
                               db: AsyncSession = Depends(get_db)):

    current_month = datetime.now().month
    current_year = datetime.now().year

    conditions = [
        extract('month', Greeting.created_at) == current_month,
        extract('year', Greeting.created_at) == current_year
    ]

    if category:
        category = validate_type(category)
        conditions.append(Greeting.type == category)

    query = select(Greeting.message, Greeting.type, Greeting.created_at) \
        .filter(*conditions) \
        .offset(offset) \
        .limit(limit)

    try:
        raw_result = await fetch_greetings(db, query, True)
        total_greetings = await count_greetings_with_conditions(db, conditions)

    except (OperationalError, SQLAlchemyError):
        raise HTTPException(status_code=500, detail='Internal Server Error')

    total_pages, offset_limit, current_page = calculateGreetingPagination(total_greetings, limit, offset)

    if offset > offset_limit:
        raise HTTPException(status_code=404, detail=f"You requested page {offset // limit + 1} which exceeds the "
                                                    f"total available pages ({total_pages}). Please request a "
                                                    f"page number between 1 and {total_pages}.")

    if not raw_result:
        raise HTTPException(status_code=404, detail='No new greetings have been added this month. Feel free to '
                                                    'explore our past greetings or check back later for new updates!')

    response = GreetingResponseModel(total_greetings=total_greetings,
                                     total_pages=total_pages,
                                     current_page=current_page,
                                     greetings=[{"message": message,
                                                 "type": type_,
                                                 "created_at": created_at.isoformat()} for message, type_, created_at
                                                in raw_result])

    return response

#
# ## Additional Considerations:
# - Ensure proper error handling for each endpoint.
# - Finish Tests for endpoints
# - add templates for the documentation aka the homepage
# - figure out how to best deploy
# - add docstrings to the code so it is easier to explain parts
# - refactor code so it more reusable and easier to work with.
