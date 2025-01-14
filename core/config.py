from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    INIT_TEMPLATE_PATH: str
    DESCRIBED_TEMPLATE_PATH: str

    class Config:
        env_file = ".env"

settings = Settings()
