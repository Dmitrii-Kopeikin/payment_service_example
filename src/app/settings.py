from granian.log import LogLevels
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy import URL


class Database(BaseModel):
    drivername: str = "postgresql+asyncpg"
    postgres_username: str = "postgres"
    postgres_password: SecretStr = SecretStr("postgres")
    host: str = "db"
    port: int = 5432
    db_name: str = "balance_service_db"


class Settings(BaseSettings):
    debug: bool = False
    log_level: LogLevels = LogLevels.info
    app_port: int = 8000
    service_name: str = "balance-service"

    database: Database = Database()

    @property
    def db_dsn(self) -> URL:
        return URL.create(
            drivername=self.database.drivername,
            username=self.database.postgres_username,
            password=self.database.postgres_password.get_secret_value(),
            host=self.database.host,
            database=self.database.db_name,
        )
