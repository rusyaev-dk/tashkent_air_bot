from dataclasses import dataclass
from typing import Optional, List

from environs import Env
from sqlalchemy.engine.url import URL
from pathlib import Path


@dataclass
class DbConfig:
    """
    Database configuration class for SQLite.
    This class holds the settings for the SQLite database, such as the file path.

    Attributes
    ----------
    db_file : str
        The file path to the SQLite database file.
    """

    db_file: str

    def __init__(self, db_file: str):
        self.db_file = db_file

    # For SQLAlchemy
    def construct_sqlalchemy_url(self) -> str:
        """
        Constructs and returns a SQLAlchemy URL for SQLite database configuration.
        """
        # SQLite URL uses the format: sqlite+aiosqlite:///absolute/path/to/database.db
        uri = URL.create(
            drivername="sqlite+aiosqlite",
            database=self.db_file
        )
        return uri.render_as_string()

    @staticmethod
    def from_env(env: "Env"):
        """
        Creates the DbConfig object from environment variables.
        """
        db_file = env.str("DB_FILE", default="./infrastructure/database/bot_db.db")
        db_file_path = Path(db_file).resolve()
        return DbConfig(db_file=str(db_file_path))


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: List[int]
    operator_ids: List[int]
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = env.list("ADMINS", subcast=int)
        operator_ids = env.list("OPERATORS", subcast=int)
        use_redis = env.bool("USE_REDIS")
        return TgBot(token=token, admin_ids=admin_ids,
                     operator_ids=operator_ids, use_redis=use_redis)


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_pass : Optional(str)
        The password used to authenticate with Redis.
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.
        """
        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(
            redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host
        )


@dataclass
class Miscellaneous:
    """
    Miscellaneous configuration class.

    This class holds settings_dialog for various other parameters.
    It merely serves as a placeholder for settings_dialog that are not part of other categories.

    Attributes
    ----------
    other_params : str, optional
        A string used to hold other various parameters as required (default is None).
    """

    other_params: str = None


@dataclass
class ApiConfig:

    api_key: str

    @staticmethod
    def from_env(env: Env):
        api_key = env.str("API_KEY")

        return ApiConfig(api_key=api_key)


@dataclass
class Config:
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings_dialog.

    Attributes
    ----------
    tg_bot : TgBot
        Holds the settings_dialog related to the Telegram Bot.
    misc : Miscellaneous
        Holds the values for miscellaneous settings_dialog.
    db : Optional[DbConfig]
        Holds the settings_dialog specific to the database (default is None).
    redis : Optional[RedisConfig]
        Holds the settings_dialog specific to Redis (default is None).
    """

    tg_bot: TgBot
    misc: Miscellaneous
    api: ApiConfig
    db: DbConfig
    redis: Optional[RedisConfig] = None


def load_config(path: str = None) -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    :param path: The path of env file from where to load the configuration variables.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """

    # Create an Env object.
    # The Env object will be used to read environment variables.
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
        db=DbConfig.from_env(env),
        redis=RedisConfig.from_env(env),
        api=ApiConfig.from_env(env),
        misc=Miscellaneous(),
    )
