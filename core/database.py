# # app/core/database.py
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from services.main.utils.caching.redis import settings
#
# SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGO_URI)
    db.db = db.client[settings.MONGO_DB_NAME]
    print(f"Connected to MongoDB database: {settings.MONGO_DB_NAME}")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")
