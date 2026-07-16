import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.auth.security import decode_token
from app.database.mongodb import get_database
from app.repositories.user_repository import UserRepository
from app.schemas.user import User
from app.services.auth_service import to_user
security=HTTPBearer()
async def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security),db:AsyncIOMotorDatabase=Depends(get_database))->User:
    try: payload=decode_token(credentials.credentials,'access')
    except jwt.PyJWTError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid or expired access token')
    user=await UserRepository(db).find_by_id(payload['sub'])
    if not user or not user['is_active']: raise HTTPException(status_code=401,detail='User not found or inactive')
    return to_user(user)
