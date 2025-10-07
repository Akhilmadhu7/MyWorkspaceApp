from fastapi import HTTPException, status, Request, Depends
from schemas.tenants import TenantCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from uuid import uuid4
import secrets, string
from repository import role_repository, tenant_repository, user_repository, TenantRepository, UserRepository, RoleRepository

class TenantService:

    '''
    '''

    def __init__(self, tenant_repo:TenantRepository, user_repo:UserRepository, role_repo:RoleRepository):
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo
        self.role_repo = role_repo

    @staticmethod
    def generate_tenant_code(length) -> str:
        characters = string.ascii_letters+string.digits
        return ''.join(secrets.choice(characters) for _ in range(length)) 


    async def create_tenant(self, request:Request, payload:TenantCreateSchema, db:AsyncSession=Depends(get_db)):

        payload:dict = payload.model_dump()
        user_email:str = payload.get("user_email")
        first_name:str = payload.get("first_name")

        tenant_payload:dict = {
            "tenant_name":f"{first_name}",
            "tenant_code": self.generate_tenant_code(15),
            "tenant_email": user_email,
            "timezone": payload.get("timezone", "UTC")
        }
        print("tenant payload", tenant_payload)
        #create tenant.
        try:
            async with db.begin():
                tenant = await self.tenant_repo.create_tenant(tenant_payload, db)
                print("tenant", tenant.tenant_id)
                owner_role = await self.role_repo.get_owner_role(db)
                #need to manage the scenario if there is no role(we need to create a owner role and assign). It will be a onetime
                #creation because the error happends only if we don't seed the roles data.
                user_payload:dict = {
                    "first_name":first_name,
                    "last_name":payload.get("last_name",None),
                    "email":user_email,
                    "tenant_id":tenant.tenant_id,
                    "role_id":owner_role.role_id,
                    "designation":payload.get("designation",None),
                    "date_of_birth":payload.get("date_of_birth",None)
                }
                await self.user_repo.create_user(user_payload, db)
                return True
        except Exception as error:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )



tenant_service = TenantService(tenant_repository, user_repository, role_repository)