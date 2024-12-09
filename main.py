from fastapi import FastAPI
from api import api_router
from api.v1 import communication, management
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
app.include_router(communication.router, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(management.router, prefix="/api/v1/management", tags=["Management"])
# app.include_router(prompt.router, prefix="/api/v1/prompt", tags=["Prompt Preparation"])
# app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
# app.include_router(personalization.router, prefix="/api/v1/personalization", tags=["Personalization"])

@app.get("/")
async def read_root():
    return {"message": "root endpoint"}
