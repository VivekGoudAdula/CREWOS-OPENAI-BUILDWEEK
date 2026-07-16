from uuid import uuid4
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.events.models import Event
from app.runtime.container import runtime
router=APIRouter(tags=['Runtime'])
@router.get('/runtime/status')
async def status():return await runtime.status()
@router.get('/agents')
@router.get('/registry')
async def agents():return await runtime.registry.list_agents()
@router.get('/agents/{agent_id}')
async def agent(agent_id:str):
    result=await runtime.registry.find_agent(agent_id)
    if not result:raise HTTPException(status_code=404,detail='Agent not found')
    return result
@router.get('/memory')
async def memory():return await runtime.memory.list_memory()
@router.get('/events')
async def events():return await runtime.event_bus.history()
@router.post('/events')
async def publish(event:Event):return await runtime.event_bus.publish(event)
@router.get('/constitution')
async def constitution():return await runtime.constitution.load()
@router.websocket('/runtime/stream')
async def event_stream(websocket:WebSocket):
    """Read-only debug stream for runtime events; agents never use this transport to communicate."""
    await websocket.accept(); subscriber_id=f'websocket:{uuid4()}'
    async def forward(event:Event)->None: await websocket.send_json(event.model_dump(mode='json'))
    await runtime.event_bus.subscribe(subscriber_id,forward)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect: pass
    finally: await runtime.event_bus.unsubscribe(subscriber_id)
