import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, UserOut, UserQuery
from models.user import User
from db.database import get_db
from config import logger

router = APIRouter()
def save(db, instance):
    db.add(instance)
    db.commit()
    db.refresh(instance)


@router.post("/", response_model=UserOut)
def create_new_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    logger.info("Checking if user already exists")
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        logger.warning("User with email %s already exists", user_in.email)
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create a new user
    new_user = User(name=user_in.name, email=user_in.email)
    logger.info("Creating new user with email %s", user_in.email)
    save(db, new_user)

    logger.info("User created successfully with ID: %s", new_user.id)
    return new_user

## to get user by email
@router.post("/get-by-email", response_model=UserOut)
def get_user_by_email(query: UserQuery, db: Session = Depends(get_db)):
    logger.info("Getting user by email: %s", query.email)
    user = db.query(User).filter(User.email == query.email).first()

    if not user:
        logger.warning("User with email %s not found", query.email)
        raise HTTPException(status_code=404, detail="User not found")

    return user
