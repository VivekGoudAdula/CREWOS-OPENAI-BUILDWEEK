from uuid import uuid4
from pydantic import BaseModel, Field
from app.schemas.common import utcnow
class Meeting(BaseModel): meeting_id:str=Field(default_factory=lambda:str(uuid4())); participants:list[str]; agenda:str; discussion:list[str]=Field(default_factory=list); action_items:list[str]=Field(default_factory=list); outcome:str|None=None; summary:str|None=None; timestamp:object=Field(default_factory=utcnow)
