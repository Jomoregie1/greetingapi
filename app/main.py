from pydantic import BaseModel
from datetime import datetime


# This represents the data that defines a greeting
class GreetingBase(BaseModel):
    message: str
    type: str


class Greeting(GreetingBase):
    greeting_id: int
    created_at: datetime
    message_hash: str

    class Config:
        orm_mode = True