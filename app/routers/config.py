from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.templating import Jinja2Templates

limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
EXPIRATION_TIME = 2_160_000
templates = Jinja2Templates(directory="app/templates")