from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.collaboration.models import Message
from app.decisions.models import Conflict
from app.events.models import Event, EventType
from app.runtime.container import runtime
router=APIRouter(tags=['Collaboration'])
@router.get('/activity')
async def activity(action:str|None=None):return await runtime.collaboration.activity(action)
@router.get('/messages')
async def messages(conversation_id:str|None=None):return await runtime.collaboration.messages(conversation_id)
@router.post('/messages',status_code=202)
async def send_message(message:Message):
    if 'broadcast' in message.recipients:
        message.recipients=[agent['agent_id'] for agent in await runtime.registry.list_agents() if agent['agent_id']!=message.sender]
    event=await runtime.collaboration.create_message(message);await runtime.event_bus.publish(Event(type=EventType.MESSAGE_SENT,source=message.sender,targets=message.recipients,payload={'message_id':message.message_id,'subject':message.subject}));await runtime.event_bus.publish(event)
    if message.message_type.value=='rejection':
        thread=await runtime.collaboration.messages(message.conversation_id);prior=next((item for item in thread if item.message_id!=message.message_id),None)
        if prior:await conflict(Conflict(topic=message.subject,context=f'Conflicting positions surfaced in conversation {message.conversation_id}.',participants=list(dict.fromkeys([prior.sender,message.sender])),positions={prior.sender:prior.content,message.sender:message.content}))
    return message
@router.get('/inbox/{agent_id}')
async def inbox(agent_id:str):return await runtime.collaboration.inbox(agent_id)
@router.get('/outbox/{agent_id}')
async def outbox(agent_id:str):return await runtime.collaboration.outbox(agent_id)
@router.post('/messages/{message_id}/read')
async def read_message(message_id:str):return {'updated':await runtime.collaboration.mark_read(message_id)}
@router.get('/decisions')
async def decisions(query:str|None=None):return await runtime.decisions.list(query)
@router.get('/meetings')
async def meetings():return runtime.collaboration._meetings
@router.get('/notifications')
async def notifications(recipient:str|None=None):return await runtime.collaboration.notifications(recipient)
@router.post('/notifications/{notification_id}/read')
async def read_notification(notification_id:str):return {'updated':await runtime.collaboration.mark_notification_read(notification_id)}
@router.post('/conflicts',status_code=202)
async def conflict(conflict:Conflict):
    decision=await runtime.decisions.create_from_conflict(conflict);meeting={'meeting_id':conflict.conflict_id,'participants':conflict.participants,'agenda':f'Resolve: {conflict.topic}','discussion':list(conflict.positions.values()),'action_items':['Review CEO decision'],'outcome':'Decision requested','summary':conflict.context};runtime.collaboration._meetings.append(meeting);ceos=[a for a in await runtime.registry.list_agents() if a['role']=='CEO'];await runtime.event_bus.publish(Event(type=EventType.CONFLICT_DETECTED,source='conflict-engine',targets=conflict.participants,payload={'decision_id':decision.decision_id,'topic':decision.topic,'project_id':decision.related_project}));await runtime.event_bus.publish(Event(type=EventType.MEETING_STARTED,source='conflict-engine',targets=conflict.participants,payload={'meeting_id':conflict.conflict_id,'topic':conflict.topic}));await runtime.event_bus.publish(Event(type=EventType.DECISION_REQUEST,source='conflict-engine',targets=[a['agent_id'] for a in ceos],payload={'decision_id':decision.decision_id,'topic':decision.topic,'project_id':decision.related_project,'options':decision.options_considered}));return decision
async def socket(channel:str,websocket:WebSocket):
    await runtime.hub.connect(channel,websocket)
    try:
        while True:await websocket.receive_text()
    except WebSocketDisconnect:pass
    finally:await runtime.hub.disconnect(channel,websocket)
@router.websocket('/ws/activity')
async def ws_activity(websocket:WebSocket):await socket('activity',websocket)
@router.websocket('/ws/messages')
async def ws_messages(websocket:WebSocket):await socket('messages',websocket)
@router.websocket('/ws/notifications')
async def ws_notifications(websocket:WebSocket):await socket('notifications',websocket)
