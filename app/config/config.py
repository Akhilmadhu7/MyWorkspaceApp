from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Config(BaseSettings):

    app_name: str = Field(default="FastApi App")
    environment:str = Field(default='dev')
    read_time_out:int = Field(default=60)
    write_time_out:int = Field(default=30)
    idle_time_out:int = Field(default=60)
    cors_allowed_origins:list = Field(default=["*"])

    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_user: Optional[str]
    db_password: Optional[str]
    db_name: Optional[str]
    ssl_mode:bool = Field(default=False)
    # max_open_connections:int
    # max_idle_connections:int
    # connection_max_life_time:int
    # connection_max_idle_time:int

    redis_host:str 
    redis_port:str
    redis_username:Optional[str] = None
    redis_password:Optional[str] = None

    rabbitmq_host:str
    rabbitmq_port:int
    rabbitmq_user:str
    rabbitmq_password:str

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def celery_backend_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def celery_broker_url(self):
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}//"
        )
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8", extra="allow",env_file='.env'
    )

config:Config = Config()
    