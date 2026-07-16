from enum import Enum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, Field
from app.schemas.common import utcnow
class MemoryCategory(str, Enum):
    SHORT_TERM='short_term'; LONG_TERM='long_term'; PROJECT='project'; COMPANY='company'; AGENT='agent'; MEETING_NOTES='meeting_notes'; ARCHITECTURE_DECISION='architecture_decision'; EVENT='event'
class MemoryEntry(BaseModel):
    id: str = Field(default_factory=lambda:str(uuid4()))
    category: MemoryCategory
    author: str
    timestamp: object = Field(default_factory=utcnow)
    tags: list[str] = Field(default_factory=list)
    importance: int = Field(default=5, ge=1, le=10)
    content: dict[str, Any]
    reference_ids: list[str] = Field(default_factory=list)
