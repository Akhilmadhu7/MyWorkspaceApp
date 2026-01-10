from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os
import uuid

class Config(BaseSettings):

    app_name: str = Field(default="FastApi App")
    server_name:str = os.getenv("HOSTNAME",f"{uuid.uuid4().hex[:8]}" )
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
    redis_password:str
    redis_db:str
    redis_username:Optional[str] = None

    rabbitmq_host:str
    rabbitmq_port:int
    rabbitmq_user:str
    rabbitmq_password:str

    jwt_algo:str
    jwt_secret_key:str
    access_token_expire_minutes:int = 100
    refresh_token_expire_minutes:int = 100

    invitation_token_expire_in_minutes:int = 10080
    forgot_password_token_expire_in_minutes:int = 60

    domain:str = Field(default="http://localhost:8000")

    EMAIL_USERNAME:str
    EMAIL_PASSWORD:str

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def redis_channel_name(self) -> str:
        return f"server-{self.server_name}"
    
    @property
    def celery_backend_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def celery_broker_url(self):
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}//"
        )
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8", extra="allow",env_file='.env'
    )

config:Config = Config()
    