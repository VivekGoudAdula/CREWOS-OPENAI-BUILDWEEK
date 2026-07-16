from datetime import timedelta
import jwt
from passlib.context import CryptContext
from app.config.settings import get_settings
from app.schemas.common import utcnow
pwd_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
def hash_password(password:str)->str:return pwd_context.hash(password)
def verify_password(password:str,password_hash:str)->bool:return pwd_context.verify(password,password_hash)
def create_token(subject:str,token_type:str,expires_delta:timedelta)->str:
    settings=get_settings(); payload={'sub':subject,'type':token_type,'iat':utcnow(),'exp':utcnow()+expires_delta}; return jwt.encode(payload,settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
def create_access_token(subject:str)->str:return create_token(subject,'access',timedelta(minutes=get_settings().access_token_expire_minutes))
def create_refresh_token(subject:str)->str:return create_token(subject,'refresh',timedelta(days=get_settings().refresh_token_expire_days))
def decode_token(token:str,expected_type:str)->dict:
    settings=get_settings(); payload=jwt.decode(token,settings.jwt_secret_key,algorithms=[settings.jwt_algorithm]);
    if payload.get('type')!=expected_type: raise jwt.InvalidTokenError('Incorrect token type')
    return payload
