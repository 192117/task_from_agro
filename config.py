from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DB: str = ''
    POSTGRES_USER: str = ''
    POSTGRES_PASSWORD: str = ''
    POSTGRES_HOST: str = '127.0.0.1'
    POSTGRES_PORT: str = 5432
    USER_SENTINEL: str = ''
    PASSWORD_SENTINEL: str = ''

    class Config:
        env_file = ".env"


settings = Settings()
DATABASE_URL = f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}' \
               f'@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
