from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.routers.config import limiter,templates

routers = APIRouter()


@routers.get("/", response_class=HTMLResponse, include_in_schema=False)
@limiter.exempt
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
