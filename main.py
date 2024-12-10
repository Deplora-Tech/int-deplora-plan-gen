from fastapi import FastAPI
from services.main.communication.api import router as communication_router
from services.main.management.api import router as management_router
from contextlib import asynccontextmanager

# Initialize FastAPI application with lifespan event handlers
app = FastAPI()
app.include_router(communication_router, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(management_router, prefix="/api/v1/management", tags=["Management"])
# app.include_router(prompt.router, prefix="/api/v1/prompt", tags=["Prompt Preparation"])
# app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
# app.include_router(personalization.router, prefix="/api/v1/personalization", tags=["Personalization"])

@app.get("/")
async def read_root():
    return {"message": "root endpoint"}
