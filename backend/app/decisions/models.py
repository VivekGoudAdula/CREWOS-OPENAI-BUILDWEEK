from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field
from app.schemas.common import utcnow
class DecisionStatus(str,Enum): REQUESTED='requested'; APPROVED='approved'; REJECTED='rejected'
class Decision(BaseModel): decision_id:str=Field(default_factory=lambda:str(uuid4())); topic:str; context:str; participants:list[str]; options_considered:list[str]; reasoning:str=''; final_decision:str|None=None; confidence:float=Field(default=0.0,ge=0,le=1); created_by:str='system'; approved_by:str|None=None; timestamp:object=Field(default_factory=utcnow); status:DecisionStatus=DecisionStatus.REQUESTED; related_project:str|None=None
class Conflict(BaseModel): conflict_id:str=Field(default_factory=lambda:str(uuid4())); topic:str; context:str; participants:list[str]; positions:dict[str,str]; related_project:str|None=None
