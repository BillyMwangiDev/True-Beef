from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://truebeef:truebeef@localhost:5432/truebeef"
    test_database_url: str = (
        "postgresql+psycopg2://truebeef:truebeef@localhost:5432/truebeef_test"
    )


settings = Settings()
