from typing import Any
from pydantic import Field
from app.schemas.common import AuditModel
class CompanyMemory(AuditModel):
    id: str
    key: str
    value: dict[str, Any] = Field(default_factory=dict)
