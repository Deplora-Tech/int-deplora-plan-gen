import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.preconditions import router as precon
from api.analyze import router as analyze
from api.chat import router as chat
from api.sockets import router as sockets
from api.executer import router as executer
from api.graph import router as graph
from api.health import router as health
from api.organization import router as organization
from api.project import router as project
from core.database import mongodb
from core.logger import logger

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Log application startup
    logger.info("Application starting up")

    yield

    # Shutdown: Close database connections and other resources
    from core.database import mongodb

    await mongodb.close()
    logger.info("Application shutting down, closed all connections")


# Initialize FastAPI application with lifespan event handlers
app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(chat, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(sockets, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(executer, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(graph, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(organization, prefix="/api/v1/communication", tags=["communication"])
app.include_router(project, prefix="/api/v1/communication", tags=["communication"])
app.include_router(analyze, prefix="/api/v1/analyzer", tags=["Analyzer"])
app.include_router(precon, prefix="/api/v1/preconditions", tags=["Preconditions"])
app.include_router(health, prefix="/api/v1", tags=["Health"])

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],  # Update with allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "root endpoint!"}
