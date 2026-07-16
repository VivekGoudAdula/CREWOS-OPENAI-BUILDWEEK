from fastapi import HTTPException, status
from app.auth.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import user_document
from app.repositories.user_repository import UserRepository
from app.schemas.user import AuthResponse, AuthTokens, User, UserCreate
def to_user(document:dict)->User:return User(id=str(document['_id']),email=document['email'],full_name=document['full_name'],is_active=document['is_active'],created_at=document['created_at'],updated_at=document['updated_at'])
class AuthService:
    def __init__(self, users:UserRepository): self.users=users
    async def register(self,payload:UserCreate)->AuthResponse:
        if await self.users.find_by_email(str(payload.email)): raise HTTPException(status_code=409,detail='Email is already registered')
        user=await self.users.create(user_document(email=str(payload.email),full_name=payload.full_name,password_hash=hash_password(payload.password))); return self._response(user)
    async def login(self,email:str,password:str)->AuthResponse:
        user=await self.users.find_by_email(email)
        if not user or not verify_password(password,user['password_hash']): raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid email or password')
        return self._response(user)
    def _response(self,document:dict)->AuthResponse:
        user=to_user(document); return AuthResponse(user=user,access_token=create_access_token(user.id),refresh_token=create_refresh_token(user.id))
    def tokens(self,user_id:str)->AuthTokens:return AuthTokens(access_token=create_access_token(user_id),refresh_token=create_refresh_token(user_id))
