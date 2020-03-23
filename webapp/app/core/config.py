import os
import yaml

from dataclasses import dataclass


@dataclass
class Settings:
    # =======================
    # Web Server settings
    # =======================
    SQLALCHEMY_DATABASE_URI: str

    # =======================
    # Web Server settings
    # =======================
    SECRET_KEY: str
    BACKEND_CORS_ORIGINS: str

    PROJECT_NAME: str = "data-api"
    SERVER_NAME: str = "localhost"
    SERVER_PORT: int = 8080
    API_V1_STR: str = "/api/v1"
    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "1qaz2wsxroot"
    USERS_OPEN_REGISTRATION: bool = True
    # token 失效时间
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    EMAILS_ENABLED:bool = False


def init_settings() -> Settings:
    current_file_path = os.path.abspath(__file__)
    settings_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    with open(os.path.join(settings_path, 'settings_prod.yml'), 'r', encoding="utf8") as f:
        settings = yaml.load(f)

    return Settings(
        SECRET_KEY=settings["server"]["secret_key"],
        SERVER_NAME=settings["server"]["server_name"],
        SERVER_PORT=settings["server"]["server_port"],
        BACKEND_CORS_ORIGINS=settings["server"]["cors_origin"],
        SQLALCHEMY_DATABASE_URI=settings["databases"]["uri"]
    )


APP_SETTINGS = init_settings()

