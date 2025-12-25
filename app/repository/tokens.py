from database.models import Token
from enums.token_enums import TokenTypeEnum
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession


class TokenRepository:

    def __init__(self, db:AsyncSession) -> None:
        self.db = db

    async def create(self, payload:dict) -> Token:
        token:Token = Token(**payload)
        self.db.add(token)
        return token


    async def get_by_token(self, token:str, token_type:TokenTypeEnum) -> Token:
        query = select(Token).where(
            Token.token == token,
            Token.token_type == token_type
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, token:"Token") -> bool:
        await self.db.delete(token)
        return True

