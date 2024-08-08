import os

from pydantic import PostgresDsn, HttpUrl
from pydantic_settings import BaseSettings


class DevConfigs(BaseSettings):
    """Development Configs"""

    POSTGRES_DSN: PostgresDsn

    SECRET_KEY: str

    ALLOWED_ORIGINS: HttpUrl

    class Config:
        env_file = ".env"
        env_prefix = "DEV_"
        env_file_encoding = "utf-8"
        extra = "ignore"


class TestConfigs(DevConfigs):
    """Test Configs"""

    class Config:
        env_prefix = "TEST_"


class ProdConfigs(DevConfigs):
    """Production Configs"""

    class Config:
        env_prefix = "PROD_"


def factory() -> DevConfigs | TestConfigs | ProdConfigs:
    """Configuration factory

    Returns:
        DevConfigs | TestConfigs | ProdConfigs: The configuration
    """
    env: str = os.environ.get("ENV", "dev")

    development = DevConfigs()
    testing = TestConfigs()
    production = ProdConfigs()

    env = env.lower()

    if env == "dev":
        return development

    if env == "test":
        return testing

    if env == "prod":
        return production

    return development


configs = factory()
