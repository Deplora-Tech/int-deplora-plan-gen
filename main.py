from fastapi import FastAPI
from api import api_router
from contextlib import asynccontextmanager
from db.database import engine, Base, connect_db, disconnect_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    Base.metadata.create_all(bind=engine)

    yield  # The application runs during this period

    await disconnect_db()

# Initialize FastAPI application with lifespan event handlers
app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

@app.get("/")
async def read_root():
    return {"message": "root endpoint"}
