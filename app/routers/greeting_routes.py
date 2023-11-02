import logging
import random
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.greeting import Greeting
from app.routers.greeting_types import GreetingType

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# Acts a dependency to manage database sessions in SQLALChemy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[Dict[str, Any]])
# rate limiter, to limit the amount of requests to the endpoint to 5 request per minute.
@limiter.limit("5/minute")
# This allows a request to be returned based on a specific type of message. The type of message is dependent on enum
# members defined to ensure better readability.
# a default limit of 10 has been added with maximum value of 100 messages can be returned at any given time.
def get_greetings(request: Request,
                  type: str = Query(..., description="Type of greeting", enum=list(GreetingType.__members__)),
                  limit: int = Query(10, description="Limit the number of greetings returned", le=100),
                  offset: int = Query(0, description="The starting point from which to retrieve the set of records. "
                                                     "An offset of 0 will start from the beginning of the dataset. "
                                                     "Use in conjunction with the 'limit' parameter to paginate "
                                                     "through records. For example, an offset of 10 with a limit of 5 "
                                                     "will retrieve records 11 through 15."),
                  db: Session = Depends(get_db)):
    # Error handling for limit,offset and type parameters.
    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset cannot be negative.")

    # validates the query type
    try:
        # Convert the Enum member name to its value
        greeting_type_value = GreetingType[type].value
        # retrieves a list of all greetings for a given type
        greetings = db.query(Greeting).filter(Greeting.type == greeting_type_value).offset(offset).limit(limit).all()
        # fetching the total number of greetings for a specified type
        total_greetings = db.query(Greeting).filter(Greeting.type == greeting_type_value).count()
        # calculation for finding the total number of pages. "rounding up divison" is used here.
        total_pages = (total_greetings + limit - 1) // limit

        # error for request for a page that doesn't exist.
        offset_limit = (total_pages * limit) - limit
        if offset > offset_limit:
            raise HTTPException(status_code=404, detail=f"You requested page {offset // limit + 1} which exceeds the "
                                                        f"total available pages ({total_pages}). Please request a "
                                                        f"page number between 1 and {total_pages}.")
    except KeyError:
        # Raises a 404 error informing the user the item they searched for was invaild.
        raise HTTPException(status_code=404, detail="This is an invalid entry type")

    # Accesses the list of greetings and returns just the message and type of the greeting as a response.
    return [{
        "total_greetings": total_greetings,
        "total_pages": total_pages,
        "current_page": offset // limit + 1,
        "message": greeting.message,
        "type": greeting.type
    } for greeting in greetings]


# TODO Error handling, for when a type parameter is not provided,
@router.get('/random', response_model=Dict[str, Any])
def get_random_greeting(request: Request
                        , type: str = Query(..., description="Type of greeting", enum=list(GreetingType.__members__))
                        , db: Session = Depends(get_db)):
    greeting_type = GreetingType[type].value
    result = db.query(Greeting.message, Greeting.created_at).filter(Greeting.type == greeting_type).all()

    if not result:
        raise HTTPException(status_code=404, detail="Greeting not found")

    response = random.choice(result)

    return {
        "message": response[0],
        "type": greeting_type,
        "status": "success",
        "timestamp": response[1]
    }


@router.get('/types', response_model=List[str])
def get_greeting_types(request: Request, db: Session = Depends(get_db)):

    try:
        result = set(type[0] for type in db.query(Greeting.type).distinct().all())

    except OperationalError as e:
        raise HTTPException(status_code=500, detail='Internal Server Error') from e

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail='Internal Server Error')
    else:
        if not result or result == {None}:
            raise HTTPException(status_code=404, detail="No types available")

        types = [name for name, member in GreetingType.__members__.items() if member.value in result]

        return types

## TODO List for Adding New Endpoints:

# - [ ] **Random Greeting**:
#   - **Endpoint**: `/greetings/random/`
#   - **Description**: Returns a random greeting from the database.
#
# - [ ] **Search Greetings**:
#   - **Endpoint**: `/greetings/search/?query=<search_term>`
#   - **Description**: Search for greetings containing a specific term or phrase.
#
# - [ ] **Greeting Stats**: - **Endpoint**: `/greetings/stats/` - **Description**: Provides statistics about the
# greetings, such as the most popular greeting type, total number of greetings, etc.
#
# - [ ] **Greeting Types**:
#   - **Endpoint**: `/greetings/types/`
#   - **Description**: List all available greeting types.
#
# - [ ] **Recent Greetings**:
#   - **Endpoint**: `/greetings/recent/?count=<number>`
#   - **Description**: Fetch a specified number of the most recent greetings added.
#
# ## Additional Considerations:
# - Remember to implement authentication & authorization if handling sensitive or user-specific data.
# - Consider rate limiting to prevent abuse.
# - Ensure proper error handling for each endpoint.
# - Update API documentation for new endpoints.
# - Write tests for each new endpoint.
# - Add caching for requently requested data
