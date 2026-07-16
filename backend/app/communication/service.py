from collections import defaultdict
from app.events.models import Event, EventType
class CommunicationEngine:
    def __init__(self): self._inboxes:dict[str,list[Event]]=defaultdict(list); self._history:dict[str,list[Event]]=defaultdict(list)
    async def send_message(self, source:str, target:str, content:dict, priority:int=5)->Event:
        event=Event(type=EventType.MESSAGE,source=source,targets=[target],payload=content,priority=priority); await self.receive_message(target,event); return event
    async def receive_message(self,agent_id:str,event:Event)->None:self._inboxes[agent_id].append(event); self._inboxes[agent_id].sort(key=lambda e:e.priority,reverse=True); self._history[agent_id].append(event)
    async def unread(self,agent_id:str)->list[Event]:return list(self._inboxes[agent_id])
    async def mark_read(self,agent_id:str,event_id:str)->bool:
        queue=self._inboxes[agent_id]; before=len(queue); self._inboxes[agent_id]=[e for e in queue if e.event_id!=event_id]; return len(queue)!=before
    async def conversation_history(self,agent_id:str)->list[Event]:return list(self._history[agent_id])
