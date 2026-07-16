from app.collaboration.models import Activity, Message, Notification
from app.events.models import Event, EventType
class CollaborationService:
    """Event-derived company communication records. Agents communicate only by EventBus events."""
    def __init__(self,registry,hub):self.registry=registry;self.hub=hub;self._messages:dict[str,Message]={};self._activities:list[Activity]=[];self._notifications:dict[str,list[Notification]]={};self._meetings=[];self._db=None
    def set_database(self,database)->None:self._db=database
    async def _store(self,collection:str,key:str,value:object)->None:
        if self._db is not None:await self._db[collection].replace_one({key:getattr(value,key)},value.model_dump(mode='json'),upsert=True)
    async def on_event(self,event:Event)->None:
        payload=event.payload;activity=Activity(agent=event.source,action=event.type.value.replace('_',' ').title(),status=event.status.value,related_project=payload.get('project_id'),related_task=payload.get('task_id'),related_decision=payload.get('decision_id'),payload=payload);self._activities.insert(0,activity);await self._store('activity','activity_id',activity);await self.hub.broadcast('activity',{'kind':'activity','data':activity.model_dump(mode='json')})
        if event.type is EventType.MESSAGE and event.event_id in self._messages:
            message=self._messages[event.event_id];await self.hub.broadcast('messages',{'kind':'message','data':message.model_dump(mode='json')})
        recipients=event.targets
        for recipient in recipients:
            note=Notification(recipient=recipient,event_type=event.type.value,title=event.type.value.replace('_',' ').title(),body=str(payload.get('subject') or payload.get('topic') or 'Company activity'),related_project=payload.get('project_id'),related_task=payload.get('task_id'),related_decision=payload.get('decision_id'));self._notifications.setdefault(recipient,[]).append(note);await self._store('notifications','notification_id',note);await self.hub.broadcast('notifications',{'kind':'notification','data':note.model_dump(mode='json')})
    async def create_message(self,message:Message)->Event:
        self._messages[message.message_id]=message;await self._store('messages','message_id',message)
        return Event(event_id=message.message_id,type=EventType.MESSAGE,source=message.sender,targets=message.recipients,priority=message.priority,payload={'conversation_id':message.conversation_id,'subject':message.subject,'content':message.content,'message_type':message.message_type.value,'reply_to':message.reply_to})
    async def messages(self,conversation_id:str|None=None)->list[Message]:return sorted([m for m in self._messages.values() if not conversation_id or m.conversation_id==conversation_id],key=lambda m:str(m.timestamp))
    async def inbox(self,agent_id:str)->list[Message]:return sorted([m for m in self._messages.values() if agent_id in m.recipients],key=lambda m:(m.status.value if hasattr(m.status,'value') else m.status,-m.priority),reverse=True)
    async def outbox(self,agent_id:str)->list[Message]:return [m for m in self._messages.values() if m.sender==agent_id]
    async def activity(self,action:str|None=None)->list[Activity]:return [a for a in self._activities if not action or a.action.lower()==action.lower()]
    async def notifications(self,recipient:str|None=None)->list[Notification]:return [n for values in self._notifications.values() for n in values if not recipient or n.recipient==recipient]
    async def mark_read(self,message_id:str)->bool:
        message=self._messages.get(message_id)
        if not message:return False
        message.status='read';return True
    async def mark_notification_read(self,notification_id:str)->bool:
        for notes in self._notifications.values():
            for note in notes:
                if note.notification_id==notification_id:note.read=True;await self._store('notifications','notification_id',note);return True
        return False
