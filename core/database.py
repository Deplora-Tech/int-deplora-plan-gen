from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from typing import Optional, Dict
from dotenv import load_dotenv
from core.config import settings
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
from services.main.communication.models import EnvType

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
    def organizations(self):
        return self.collection("organizations")

    @property
    def org_env_variables(self):
        return self.collection("org_env_variables")

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

    async def find_one(self, *args, **kwargs):
        await mongodb.connect()
        return await mongodb.collection(self.collection_name).find_one(*args, **kwargs)

    async def update_one(self, *args, **kwargs):
        await mongodb.connect()
        return await mongodb.collection(self.collection_name).update_one(
            *args, **kwargs
        )

    async def delete_one(self, *args, **kwargs):
        await mongodb.connect()
        return await mongodb.collection(self.collection_name).delete_one(
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
organizations = CollectionWrapper("organizations")
org_env_variables = CollectionWrapper("org_env_variables")
projects = CollectionWrapper("projects")
project_env_variables = CollectionWrapper("project_env_variables")


class EnvironmentManager:
    def __init__(self):
        self._salt = os.environ.get("ENCRYPTION_SALT", "").encode()
        if not self._salt:
            self._salt = os.urandom(16)
            logger.warning(
                "No salt in env. Generated one. Will break decryption of saved data."
            )

        encryption_key = (
            os.environ.get("ENCRYPTION_KEY", "")
            or "fallback_encryption_key_for_development_only"
        )
        if encryption_key == "fallback_encryption_key_for_development_only":
            logger.warning("Using fallback encryption key. Don't use in production.")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=self._salt, iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        self._cipher = Fernet(key)

        self.collection_map = {
            EnvType.ORG: org_env_variables,
            EnvType.PROJECT: project_env_variables,
        }

    def _encrypt(self, value: str) -> str:
        return self._cipher.encrypt(value.encode()).decode() if value else value

    def _decrypt(self, value: str) -> str:
        return self._cipher.decrypt(value.encode()).decode() if value else value

    def _get_collection(self, env_type: EnvType):
        return self.collection_map.get(env_type)

    # --------- Unified Interface ---------

    async def set_variable(
        self, env_type: EnvType, id_value: str, key: str, value: str
    ) -> bool:
        try:
            collection = self._get_collection(env_type)
            field = f"{env_type.value}_id"
            encrypted_value = self._encrypt(value)
            filter_query = {field: id_value, "key": key}

            existing = await collection.find_one(filter_query)
            if existing:
                result = await collection.update_one(
                    filter_query, {"$set": {"value": encrypted_value}}
                )
                return result.modified_count > 0
            else:
                result = await collection.insert_one(
                    {field: id_value, "key": key, "value": encrypted_value}
                )
                return result.inserted_id is not None
        except Exception as e:
            logger.error(f"Error setting {env_type.value} variable: {e}")
            return False

    async def get_variable(
        self, env_type: EnvType, id_value: str, key: str
    ) -> Optional[str]:
        try:
            collection = self._get_collection(env_type)
            field = f"{env_type.value}_id"
            result = await collection.find_one({field: id_value, "key": key})
            return (
                self._decrypt(result["value"]) if result and "value" in result else None
            )
        except Exception as e:
            logger.error(f"Error getting {env_type.value} variable: {e}")
            return None

    async def get_all_variables(
        self, env_type: EnvType, id_value: str
    ) -> Dict[str, str]:
        try:
            collection = self._get_collection(env_type)
            field = f"{env_type.value}_id"
            cursor = await collection.find({field: id_value})
            result = {}
            async for doc in cursor:
                if "key" in doc and "value" in doc:
                    result[doc["key"]] = self._decrypt(doc["value"])
            return result
        except Exception as e:
            logger.error(f"Error retrieving all {env_type.value} variables: {e}")
            return {}

    async def delete_variable(self, env_type: EnvType, id_value: str, key: str) -> bool:
        try:
            collection = self._get_collection(env_type)
            field = f"{env_type.value}_id"
            result = await collection.delete_one({field: id_value, "key": key})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting {env_type.value} variable: {e}")
            return False

    async def save_multiple_variables(
        self, env_type: EnvType, id_value: str, variables: Dict[str, str]
    ) -> bool:
        try:
            for key, value in variables.items():
                await self.set_variable(env_type, id_value, key, value)
            return True
        except Exception as e:
            logger.error(f"Error saving multiple {env_type.value} variables: {e}")
            return False


env_manager = EnvironmentManager()


async def ping_database():
    return await mongodb.ping()
