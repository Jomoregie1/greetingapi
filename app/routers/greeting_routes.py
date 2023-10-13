from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.greeting import Greeting
from app.routers.greeting_types import GreetingType

router = APIRouter()


# Acts a dependency to manage database sessions in SQLALChemy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/greetings/", response_model=List[Dict[str, Any]])
# This allows a request to be returned based on a specific type of message. The type of message is dependent on enum
# members defined to ensure better readability.
# a default limit of 10 has been added with maximum value of 100 messages can be returned at any given time.
def get_greetings(type: str = Query(..., description="Type of greeting", enum=list(GreetingType.__members__)),
                  limit: int = Query(10, description="Limit the number of greetings returned", le=100),
                  offset: int = Query(0, description="The starting point from which to retrieve the set of records. "
                                                     "An offset of 0 will start from the beginning of the dataset. "
                                                     "Use in conjunction with the 'limit' parameter to paginate "
                                                     "through records. For example, an offset of 10 with a limit of 5 "
                                                     "will retrieve records 11 through 15."),
                  db: Session = Depends(get_db)):
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
