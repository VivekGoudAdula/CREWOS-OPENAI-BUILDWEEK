from datetime import datetime, timezone
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field
T=TypeVar('T')
def utcnow() -> datetime: return datetime.now(timezone.utc)
class TimestampedModel(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
class AuditModel(TimestampedModel):
    created_by: str | None = None
    updated_by: str | None = None
class APIResponse(BaseModel, Generic[T]):
    data: T
    message: str = 'Success'
class Pagination(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)
    total: int = 0
class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
