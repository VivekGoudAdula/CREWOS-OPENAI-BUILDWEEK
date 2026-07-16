import asyncio
from collections import defaultdict
from fastapi import WebSocket
class RealtimeHub:
    def __init__(self):self._channels:dict[str,set[WebSocket]]=defaultdict(set);self._lock=asyncio.Lock()
    async def connect(self,channel:str,websocket:WebSocket)->None:
        await websocket.accept();self._channels[channel].add(websocket);await websocket.send_json({'kind':'connected','channel':channel})
    async def disconnect(self,channel:str,websocket:WebSocket)->None:self._channels[channel].discard(websocket)
    async def broadcast(self,channel:str,payload:dict)->None:
        stale=[]
        for websocket in list(self._channels[channel]):
            try:await websocket.send_json(payload)
            except Exception:stale.append(websocket)
        for websocket in stale:self._channels[channel].discard(websocket)
