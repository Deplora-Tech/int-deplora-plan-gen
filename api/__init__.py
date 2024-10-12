from fastapi import APIRouter, FastAPI
from api.user import router as user_router  # Ensure correct import of user_router
api_router = APIRouter()

# Include subroutes (e.g., user routes)
api_router.include_router(user_router, prefix="/users", tags=["users"])
