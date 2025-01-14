import os
from fastapi import FastAPI
from services.main.communication.api import router as communication_router
from services.main.analyzer.api import router as analyzer_router
from fastapi.middleware.cors import CORSMiddleware
from core.database import connect_to_mongo, close_mongo_connection

# Initialize FastAPI application with lifespan event handlers
app = FastAPI()

# Include routers
app.include_router(communication_router, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(analyzer_router, prefix="/api/v1/analyzer", tags=["Analyzer"])

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB's connection on startup
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

# MongoDB's disconnection on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "root endpoint"}
