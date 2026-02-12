from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central config for the backend.

    You can later add:
    - OPENAI_API_KEY (if you use an LLM)
    - DATABASE_URL
    - REDIS_URL
    - MODEL_PATH overrides
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Paths (relative to repo root when running)
    data_path: str = "data/synthetic_course_data.csv"
    artifacts_dir: str = "artifacts"

    # Chat behavior
    max_context_turns: int = 8


settings = Settings()
