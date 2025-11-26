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


db_config = DatabaseConfig()
