from fastapi import HTTPException, status, Request
from schemas.tenants import TenantCreateSchema
from uuid import uuid4, UUID
import secrets, string
from repository import TenantRepository, UserRepository, RoleRepository
from helpers import generate_password


class TenantService:

    '''
    '''

    def __init__(self, tenant_repo:TenantRepository, user_repo:UserRepository = None, role_repo:RoleRepository = None):
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo
        self.role_repo = role_repo

    @staticmethod
    def generate_tenant_code(length) -> str:
        characters = string.ascii_letters+string.digits
        return ''.join(secrets.choice(characters) for _ in range(length)) 


    async def create_tenant(self, request:Request, payload:TenantCreateSchema):

        payload:dict = payload.model_dump()
        user_email:str = payload.get("user_email")
        first_name:str = payload.get("first_name")

        tenant_payload:dict = {
            "tenant_name":f"{first_name}",
            "tenant_code": self.generate_tenant_code(15),
            "tenant_email": user_email,
            "timezone": payload.get("timezone", "UTC")
        }
        #create tenant.
        try:
            async with self.tenant_repo.db.begin():
                tenant = await self.tenant_repo.create_tenant(tenant_payload)
                owner_role = await self.role_repo.get_owner_role()
                user_id:UUID = uuid4()
                password:str = generate_password(tenant.tenant_id, user_id)
                #need to manage the scenario if there is no role(we need to create a owner role and assign). It will be a onetime
                #creation because the error happends only if we don't seed the roles data.
                user_payload:dict = {
                    "first_name":first_name,
                    "last_name":payload.get("last_name",None),
                    "email":user_email,
                    "tenant_id":tenant.tenant_id,
                    "role_id":owner_role.role_id,
                    "designation":payload.get("designation",None),
                    "date_of_birth":payload.get("date_of_birth",None),
                    "password":password,
                    "username":user_email,
                    "user_id":user_id,
                    "is_active":True
                }
                await self.user_repo.create_user(user_payload)
                await self.tenant_repo.db.commit()
                return True
        except Exception as error:
            await self.tenant_repo.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )

    async def get_tenant(self, request:Request, tenant_id:UUID):
        
        #authorization might be needed depends on the requirements as we grow.
        tenant = await self.tenant_repo.get_tenant_by_tenant_id(tenant_id)
        # return TenantResponse.from_orm(tenant)
        return tenant
