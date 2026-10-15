from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Climate Hazard Analyzer API"
    api_prefix: str = "/api"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "climate_hazard_analyzer"
    frontend_origin: str = "http://localhost:5173"
    open_meteo_base_url: str = "https://archive-api.open-meteo.com/v1/archive"
    reference_start_year: int = 1991
    reference_end_year: int = 2020

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
