from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from typing import Optional
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

logger = logging.getLogger(__name__)


class MongoDBConnection:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._client: Optional[AsyncIOMotorClient] = None
            self._db: Optional[AsyncIOMotorDatabase] = None
            self._initialized = True
            self._collections = {}

    async def connect(self) -> None:
        if self._client is None:
            try:
                self._client = AsyncIOMotorClient(
                    settings.ATLAS_MONGO_URI,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                )
                await self._client.admin.command("ping")
                self._db = self._client[settings.MONGO_DB_NAME]
                logger.info(f"Connected to MongoDB database: {settings.MONGO_DB_NAME}")
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.error(f"MongoDB connection error: {e}")
                raise

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            self._collections = {}
            logger.info("MongoDB connection closed")

    def collection(self, name: str):

        if self._db is None:
            raise ValueError("Not connected to MongoDB. Call connect() first.")

        if name not in self._collections:
            self._collections[name] = self._db[name]

        return self._collections[name]

    @property
    def db(self) -> AsyncIOMotorDatabase:

        if self._db is None:
            raise ValueError("Not connected to MongoDB. Call connect() first.")
        return self._db

    @property
    def client(self) -> AsyncIOMotorClient:

        if self._client is None:
            raise ValueError("Not connected to MongoDB. Call connect() first.")
        return self._client

    @property
    def analysis_results(self):
        return self.collection("analysis_results")

    @property
    def templates(self):
        return self.collection("templates")

    @property
    def users(self):
        return self.collection("users")

    @property
    def projects(self):
        return self.collection("projects")

    async def ping(self) -> bool:

        try:
            if self._client is not None:
                await self._client.admin.command("ping")
                return True
            return False
        except Exception:
            return False


mongodb = MongoDBConnection()


class CollectionWrapper:
    def __init__(self, collection_name):
        self.collection_name = collection_name

    async def find(self, *args, **kwargs):
        await mongodb.connect()
        return await mongodb.collection(self.collection_name).find(*args, **kwargs)

    async def insert_one(self, *args, **kwargs):
        await mongodb.connect()
        return await mongodb.collection(self.collection_name).insert_one(
            *args, **kwargs
        )

    async def count_documents(self, *args, **kwargs):
        await mongodb.connect()
        return await mongodb.collection(self.collection_name).count_documents(
            *args, **kwargs
        )

    async def aggregate(self, *args, **kwargs):
        await mongodb.connect()
        return await mongodb.collection(self.collection_name).aggregate(*args, **kwargs)


analysis_results = CollectionWrapper("analysis_results")
projects = CollectionWrapper("projects")


async def ping_database():
    return await mongodb.ping()
