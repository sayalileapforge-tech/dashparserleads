"""Configuration management using environment variables."""
from pydantic_settings import BaseSettings
from urllib.parse import quote


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "insurance_leads"

    # Meta API
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_page_id: str = ""
    meta_page_access_token: str = ""
    meta_lead_form_id: str = ""

    # API
    api_port: int = 3000
    api_debug: bool = False
    api_host: str = "127.0.0.1"

    # Environment
    environment: str = "development"

    @property
    def database_url(self) -> str:
        """Generate database connection URL with URL-encoded password."""
        encoded_password = quote(self.mysql_password, safe='')
        return (
            f"mysql+pymysql://{self.mysql_user}:{encoded_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Load settings from environment
settings = Settings()
