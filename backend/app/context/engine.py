from app.communication.service import CommunicationEngine
from app.constitution.service import ConstitutionService
from app.memory.service import MemoryService
from app.runtime.event_bus import EventBus
class ContextEngine:
    def __init__(self,memory:MemoryService,communications:CommunicationEngine,constitution:ConstitutionService,event_bus:EventBus):self.memory=memory;self.communications=communications;self.constitution=constitution;self.event_bus=event_bus
    async def assemble(self,agent:object)->dict:
        return {'relevant_memory':[m.model_dump() for m in await self.memory.retrieve_context(agent.agent_id)],'current_task':agent.current_task,'conversation_history':[e.model_dump() for e in await self.communications.conversation_history(agent.agent_id)],'constitution':(await self.constitution.load()).model_dump(),'recent_events':[e.model_dump() for e in await self.event_bus.history(limit=20)],'current_goals':agent.goals}
