from fastapi import FastAPI
from app.routers import greeting_routes


app = FastAPI()
app.include_router(greeting_routes.router)

