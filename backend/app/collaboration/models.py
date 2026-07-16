from enum import Enum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, Field
from app.schemas.common import utcnow
class MessageType(str,Enum): QUESTION='question'; ANSWER='answer'; SUGGESTION='suggestion'; APPROVAL='approval'; REJECTION='rejection'; REQUEST='request'; NOTIFICATION='notification'; WARNING='warning'; DECISION='decision'; MEETING='meeting'
class MessageStatus(str,Enum): UNREAD='unread'; READ='read'
class Message(BaseModel):
    message_id:str=Field(default_factory=lambda:str(uuid4())); conversation_id:str=Field(default_factory=lambda:str(uuid4())); sender:str; recipients:list[str]; timestamp:object=Field(default_factory=utcnow); priority:int=Field(default=5,ge=1,le=10); message_type:MessageType; subject:str; content:str; attachments:list[dict[str,Any]]=Field(default_factory=list); status:MessageStatus=MessageStatus.UNREAD; reply_to:str|None=None
class Notification(BaseModel): notification_id:str=Field(default_factory=lambda:str(uuid4())); recipient:str; event_type:str; title:str; body:str; timestamp:object=Field(default_factory=utcnow); read:bool=False; related_project:str|None=None; related_task:str|None=None; related_decision:str|None=None
class Activity(BaseModel): activity_id:str=Field(default_factory=lambda:str(uuid4())); timestamp:object=Field(default_factory=utcnow); agent:str; action:str; status:str; related_project:str|None=None; related_task:str|None=None; related_decision:str|None=None; payload:dict[str,Any]=Field(default_factory=dict)
