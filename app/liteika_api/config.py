from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str
    
    OPENAI_API_KEY: str
    
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=''
    )
    

config = Settings()  # type: ignore