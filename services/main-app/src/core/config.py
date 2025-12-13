from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml", ".env"],
    envvar_prefix=False,
)


class DatabaseConfig:
    @property
    def url(self) -> str:
        db = settings.db_settings
        return (
            f"postgresql+asyncpg://{db.db_user}:{db.db_password}"
            f"@{db.db_host}:{db.db_port}/{db.db_name}"
        )


class AuthSettings:
    @property
    def secret_key(self) -> str:
        return settings.auth_settings.sekret_key

    @property
    def algorithm(self) -> str:
        return settings.auth_settings.algorithm

    @property
    def access_token_expire_minutes(self) -> int:
        return settings.auth_settings.access_token_expire_minutes

    @property
    def refresh_token_expire_days(self) -> int:
        return settings.auth_settings.get("refresh_token_expire_days", 30)


db_config = DatabaseConfig()
auth_config = AuthSettings()
