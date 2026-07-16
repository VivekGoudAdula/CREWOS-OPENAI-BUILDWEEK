from pydantic import BaseModel, EmailStr, Field
from app.schemas.common import TimestampedModel
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)
class UserLogin(BaseModel):
    email: EmailStr
    password: str
class User(TimestampedModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool = True
class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
class AuthResponse(AuthTokens): user: User
class RefreshRequest(BaseModel): refresh_token: str
