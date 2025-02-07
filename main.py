import os
from fastapi import FastAPI
from api import chat, sockets, executer, graph, analyze
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI application with lifespan event handlers
app = FastAPI()

# Include routers
app.include_router(chat.router, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(
    sockets.router, prefix="/api/v1/communication", tags=["Communication"]
)
app.include_router(
    executer.router, prefix="/api/v1/communication", tags=["Communication"]
)
app.include_router(graph.router, prefix="/api/v1/communication", tags=["Communication"])
app.include_router(analyze.router, prefix="/api/v1/analyzer", tags=["Analyzer"])

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
    return {"message": "root endpoint"}
