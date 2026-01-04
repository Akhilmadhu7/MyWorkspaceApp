from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from typing import Dict, Optional
from fastapi import Request
from sqlalchemy import text
from config.config import config
from contextlib import asynccontextmanager

class DatabaseConnectionManager:

    _instance = None

    def __init__(self):
        self.engines: Dict[str, AsyncEngine] = {}
        self.async_sessions_factory:Dict[str, async_sessionmaker] = {}
        return None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    
    def get_engine(self,
        db_url:str,
        pool_size:int = 10, 
        pool_timeout:int = 30,
        max_overflow:int = 10,
        pool_recycle:int = 1800,
        echo:bool = False,
        pool_pre_ping:bool = False
        ) -> None:
        if db_url not in self.engines:
            connect_args:dict = {
                    "server_settings": {
                        "application_name":"boiler-plate"
                    }
                }
            engine  = create_async_engine(
                url=db_url,
                pool_size=pool_size,
                pool_recycle = pool_recycle,
                pool_timeout = pool_timeout,
                max_overflow = max_overflow,
                echo=echo,
                pool_pre_ping=pool_pre_ping,
                connect_args = connect_args
            )
            self.engines[db_url] = engine
        return self.engines[db_url]

    
    def get_async_session(self, db_url:str):
        '''
        method takes db_url as the parameter and returns the async_session object.
        '''
        if db_url not in self.async_sessions_factory:
            engine = self.get_engine(db_url)
            async_session =  async_sessionmaker(bind=engine, expire_on_commit=False)
            self.async_sessions_factory[db_url] = async_session
        return self.async_sessions_factory[db_url]
    
    
    async def connect_to_db(self):
        '''
        This method should be invoked when the app starts by providing the default db env variables.
        It then creates an engine and async-session and save it in memory for future use.
        Also it ping to the db and raise error if ping fails. 
        '''
        db_url:str = config.database_url
        engine:AsyncEngine = self.get_engine(db_url)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception as error:
            raise error
    
    @property
    def get_default_async_session(self):
        '''
        method returns the default async session for the default database.
        '''
        return self.get_async_session(config.database_url)

    async def clean_up_engines(self):
        '''
        method should be invoked when the app shut down and it deletes all the engines and session saved in the 
        memory. Also it dispose all the available engines.
        '''
        for engine in self.engines.values():
            await engine.dispose()
        self.engines.clear()
        self.async_sessions_factory.clear()

    

#initialize the DatabaseConnectionManager instance globally.
db_manager:DatabaseConnectionManager = DatabaseConnectionManager()


async def get_db():
    async_session = db_manager.get_default_async_session
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

    


