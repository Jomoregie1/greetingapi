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


# This will fetch greetings based of a type
@router.get("/greetings/")
# This allows a request to be returned based on a specific type of message. The type of message is dependent on enum
# members defined to ensure better readability.
def get_greetings(type: str = Query(..., description="Type of greeting", enum=list(GreetingType.__members__)),
                  db: Session = Depends(get_db)):
    # validates the query type
    try:
        # Convert the Enum member name to its value
        greeting_type_value = GreetingType[type].value
    except KeyError:
        # Raises a 404 error informing the user the item they searched for was invaild.
        raise HTTPException(status_code=404, detail="This is an invalid entry type")
    # Use the actual value in the query
    return db.query(Greeting).filter(Greeting.type == greeting_type_value).all()
