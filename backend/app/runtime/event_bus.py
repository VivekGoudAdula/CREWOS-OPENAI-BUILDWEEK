import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from app.events.models import Event, EventStatus
Subscriber=Callable[[Event],Awaitable[None]]
class EventBus:
    """In-process asynchronous pub/sub runtime. Routing is subscription based, never role based."""
    def __init__(self):self._subscribers:dict[str,Subscriber]={};self._subscriptions:dict[str,set[str]]=defaultdict(set);self._observers:list[Subscriber]=[];self._history:list[Event]=[];self._lock=asyncio.Lock()
    def add_observer(self,observer:Subscriber)->None:self._observers.append(observer)
    async def subscribe(self,subscriber_id:str,handler:Subscriber,event_types:set[str]|None=None)->None:
        self._subscribers[subscriber_id]=handler; self._subscriptions[subscriber_id]=event_types or {'*'}
    async def unsubscribe(self,subscriber_id:str)->None:self._subscribers.pop(subscriber_id,None);self._subscriptions.pop(subscriber_id,None)
    async def publish(self,event:Event)->Event:
        async with self._lock:self._history.append(event)
        recipients=[handler for identifier,handler in self._subscribers.items() if identifier!=event.source and (not event.targets or identifier in event.targets) and ('*' in self._subscriptions[identifier] or event.type.value in self._subscriptions[identifier])]
        if recipients:
            results=await asyncio.gather(*(handler(event) for handler in recipients),return_exceptions=True); event.status=EventStatus.FAILED if any(isinstance(r,Exception) for r in results) else EventStatus.PROCESSED
        else:event.status=EventStatus.DISPATCHED
        await asyncio.gather(*(observer(event) for observer in self._observers),return_exceptions=True)
        return event
    async def history(self,limit:int=100)->list[Event]:return list(self._history[-limit:])
