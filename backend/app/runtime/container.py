from app.communication.service import CommunicationEngine
from app.constitution.service import ConstitutionService
from app.context.engine import ContextEngine
from app.memory.service import MemoryService
from app.reasoning.provider import DeterministicReasoningProvider
from app.registry.service import AgentRegistry
from app.runtime.event_bus import EventBus
from app.planning.provider import DeterministicPlanningProvider
from app.planning.service import ProjectPlanningService
from app.decisions.service import DecisionService
from app.realtime.hub import RealtimeHub
from app.collaboration.service import CollaborationService
from app.engineering.service import EngineeringService
from app.engineering.provider import AzureOpenAICodeGenerationProvider
from app.qa.service import QAService
class RuntimeContainer:
    def __init__(self):
        self.event_bus=EventBus();self.memory=MemoryService();self.registry=AgentRegistry();self.communications=CommunicationEngine();self.constitution=ConstitutionService();self.reasoning=DeterministicReasoningProvider();self.context=ContextEngine(self.memory,self.communications,self.constitution,self.event_bus);self.projects=ProjectPlanningService();self.planning_provider=DeterministicPlanningProvider();self.hub=RealtimeHub();self.collaboration=CollaborationService(self.registry,self.hub);self.decisions=DecisionService();self.engineering=EngineeringService(AzureOpenAICodeGenerationProvider());self.qa=QAService();self.event_bus.add_observer(self.collaboration.on_event)
        self.agents: list[object] = []
    async def status(self)->dict:
        health=await self.registry.health_check();return {'status':'running','event_count':len(await self.event_bus.history()),'memory_count':len(await self.memory.list_memory()),**health}
runtime=RuntimeContainer()
