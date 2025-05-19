from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    ANTHROPIC_API_KEY: str
    DEEPSEEK_API_KEY: str
    REPO_PATH: str
    JENKINS_URL: str
    JENKINS_USERNAME: str
    JENKINS_PASSWORD: str
    JENKINS_API_TOKEN: str
    GRAPH_GENERATOR_URL: str
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str

    MONGO_URI: str
    MONGO_DB_NAME: str
    INIT_TEMPLATE_PATH: str
    DESCRIBED_TEMPLATE_PATH: str
    ATLAS_MONGO_URI: str
    GITHUB_ACCESS_TOKEN: str
    NGROK_URL: str

    GOOGLE_API_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str


    class Config:
        env_file = ".env"

settings = Settings()
