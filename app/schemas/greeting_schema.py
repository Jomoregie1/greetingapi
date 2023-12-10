from typing import List, Any, Dict
from pydantic import BaseModel
from datetime import datetime
from app.routers.greeting_types import GreetingType


# This represents the data that defines a greeting
class GreetingBase(BaseModel):
    message: str
    type: str


# Validates incomming request data for an API endpoint that retrieves greetings.
class GreetingRequestModel(BaseModel):
    type: GreetingType
    limit: int
    offset: int


# Structures the data sent back to the user.
class GreetingResponseModel(BaseModel):
    total_greetings: int
    total_pages: int
    current_page: int
    greetings: List[Dict[str, Any]]


#  This defines my greeting table with the additional fields.
class Greeting(GreetingBase):
    greeting_id: int
    created_at: datetime
    message_hash: str

    class ConfigDict:
        from_attributes = True
