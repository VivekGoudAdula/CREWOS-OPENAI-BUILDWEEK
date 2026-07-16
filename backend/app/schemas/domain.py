from typing import Any
from pydantic import BaseModel, Field
from app.schemas.common import AuditModel
class Project(AuditModel): id:str; name:str; description:str|None=None; owner_id:str
class Task(AuditModel): id:str; project_id:str; title:str; status:str='pending'
class Agent(AuditModel): id:str; name:str; role:str; status:str='inactive'
class Event(AuditModel): id:str; event_type:str; payload:dict[str,Any]=Field(default_factory=dict)
