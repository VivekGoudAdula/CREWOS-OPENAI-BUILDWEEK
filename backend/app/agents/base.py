from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4
from app.events.models import Event, EventType
from app.memory.models import MemoryCategory, MemoryEntry
from app.schemas.common import utcnow
class AgentState(str,Enum): INITIALIZING='INITIALIZING'; IDLE='IDLE'; THINKING='THINKING'; REASONING='REASONING'; WAITING='WAITING'; WORKING='WORKING'; BLOCKED='BLOCKED'; REVIEWING='REVIEWING'; COMPLETED='COMPLETED'; OFFLINE='OFFLINE'
class BaseAgent(ABC):
    """Reusable autonomous employee contract. Collaboration happens exclusively via EventBus."""
    def __init__(self,*,name:str,role:str,department:str,description:str,goals:list[str],responsibilities:list[str],capabilities:list[str],priority:int=5,agent_id:str|None=None):
        self.agent_id=agent_id or str(uuid4());self.name=name;self.role=role;self.department=department;self.description=description;self.goals=goals;self.responsibilities=responsibilities;self.capabilities=capabilities;self.priority=priority;self.status=AgentState.INITIALIZING;self.state=AgentState.INITIALIZING;self.current_task:dict[str,Any]|None=None;self.memory_reference=self.agent_id;self.inbox:list[str]=[];self.outbox:list[str]=[];self.available_tools:list[str]=[];self.context_window=32_000;self.created_time=utcnow();self.updated_time=utcnow();self._runtime:Any=None
    async def initialize(self,runtime:Any)->None:
        self._runtime=runtime;self.status=self.state=AgentState.IDLE;await runtime.registry.register_agent(self);await runtime.event_bus.subscribe(self.agent_id,self.receive_event);await self.publish_event(Event(type=EventType.AGENT_ONLINE,source=self.agent_id,payload={'agent_id':self.agent_id}))
    async def think(self)->dict[str,Any]:self.state=AgentState.THINKING;return await self.load_context()
    async def reason(self)->dict[str,Any]:self.state=AgentState.REASONING;return await self._runtime.reasoning.reason(await self.load_context())
    async def decide(self)->dict[str,Any]:return await self.reason()
    async def execute(self)->None:self.state=AgentState.WORKING
    async def receive_event(self,event:Event)->None:
        if event.type is EventType.AGENT_STATUS_UPDATED:return
        self.inbox.append(event.event_id);await self._runtime.communications.receive_message(self.agent_id,event)
        context=await self.think(); decision=await self.reason()
        await self.update_memory(MemoryCategory.EVENT,{'event_id':event.event_id,'type':event.type.value,'payload':event.payload,'reasoning':decision})
        # SYSTEM_EVENT messages are terminal observations. Re-publishing a project
        # observation for one would recursively flood the event bus and starve real
        # planning events such as CEO_STRATEGY_CREATED.
        if event.payload.get('project_id') and event.type is not EventType.SYSTEM_EVENT:
            await self.publish_event(Event(type=EventType.SYSTEM_EVENT,source=self.agent_id,payload={'project_id':event.payload['project_id'],'action':'project_context_reviewed','agent_id':self.agent_id,'outcome':decision.get('outcome','reviewed'),'work_output':decision}))
        # Acknowledge non-system work through the bus. SYSTEM_EVENT is deliberately terminal to prevent feedback loops.
        if event.type is not EventType.SYSTEM_EVENT:
            await self.publish_event(Event(type=EventType.SYSTEM_EVENT,source=self.agent_id,targets=[event.source],payload={'related_event_id':event.event_id,'outcome':decision.get('outcome','assessed')}))
        self.state=AgentState.WAITING; self.status=AgentState.WAITING; await self.heartbeat()
    async def publish_event(self,event:Event)->Event:self.outbox.append(event.event_id);return await self._runtime.event_bus.publish(event)
    async def receive_message(self,event:Event)->None:await self.receive_event(event)
    async def send_message(self,target:str,content:dict[str,Any],priority:int=5)->Event:return await self.publish_event(Event(type=EventType.MESSAGE,source=self.agent_id,targets=[target],payload=content,priority=priority))
    async def update_memory(self,category:MemoryCategory,content:dict[str,Any])->MemoryEntry:
        return await self._runtime.memory.create_memory(MemoryEntry(category=category,author=self.agent_id,content=content))
    async def load_context(self)->dict[str,Any]:return await self._runtime.context.assemble(self)
    async def heartbeat(self)->None:await self._runtime.registry.heartbeat(self.agent_id,self.state.value)
    async def set_state(self,state:AgentState)->None:
        self.state=self.status=state; self.updated_time=utcnow()
        if self._runtime:
            await self.heartbeat();await self.publish_event(Event(type=EventType.AGENT_STATUS_UPDATED,source=self.agent_id,payload={'agent_id':self.agent_id,'state':state.value}))
    async def shutdown(self)->None:
        if self._runtime:await self.publish_event(Event(type=EventType.AGENT_OFFLINE,source=self.agent_id,payload={'agent_id':self.agent_id}));await self._runtime.event_bus.unsubscribe(self.agent_id);await self._runtime.registry.remove_agent(self.agent_id)
        self.status=self.state=AgentState.OFFLINE
