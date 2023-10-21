from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from app.routers.greeting_routes import get_db
from app.main import app

DATABASE_URL = config('TEST_DATABASE_URL')
engine = create_engine(DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test client allows you to send http requests to your fastapi application to recieve responses.
client = TestClient(app)


# This is our test database, the following function defines a context manager function, which manages the lifecycle
# of our database session.
def override_get_db():
    # try and except used to ensure cleanup action.
    db = TestSessionLocal()
    try:
        # makes the function a generator based context manager allowing it to use the session to make database queries
        yield db
    finally:
        db.close()


# This is overriding the dependency for get_db with override_get_db.
app.dependency_overrides[get_db] = override_get_db
