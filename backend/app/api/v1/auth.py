import jwt
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth.dependencies import get_current_user
from app.auth.security import decode_token
from app.database.mongodb import get_database
from app.repositories.user_repository import UserRepository
from app.schemas.user import AuthResponse, RefreshRequest, User, UserCreate, UserLogin
from app.services.auth_service import AuthService
router=APIRouter(prefix='/auth',tags=['Authentication'])
def service(db:AsyncIOMotorDatabase=Depends(get_database))->AuthService:return AuthService(UserRepository(db))
@router.post('/register',response_model=AuthResponse,status_code=201)
async def register(payload:UserCreate,auth:AuthService=Depends(service)):return await auth.register(payload)
@router.post('/login',response_model=AuthResponse)
async def login(payload:UserLogin,auth:AuthService=Depends(service)):return await auth.login(str(payload.email),payload.password)
@router.post('/refresh')
async def refresh(payload:RefreshRequest,auth:AuthService=Depends(service)):
    try: claims=decode_token(payload.refresh_token,'refresh')
    except jwt.PyJWTError: raise HTTPException(status_code=401,detail='Invalid or expired refresh token')
    return auth.tokens(claims['sub'])
@router.post('/logout',status_code=204)
async def logout(): return None
@router.get('/me',response_model=User)
async def me(user:User=Depends(get_current_user)):return user
