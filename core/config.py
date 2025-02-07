from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    INIT_TEMPLATE_PATH: str
    DESCRIBED_TEMPLATE_PATH: str
    GROQ_API_KEY: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    ANTHROPIC_API_KEY: str
    DEEPSEEK_API_KEY: str
    REPO_PATH: str
    JENKINS_URL: str
    JENKINS_USER: str
    JENKINS_API_TOKEN: str
    ATLAS_MONGO_URI: str

    class Config:
        env_file = ".env"

settings = Settings()
