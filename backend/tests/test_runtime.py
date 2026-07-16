import pytest
from app.agents.base import BaseAgent, AgentState
from app.events.models import Event, EventType
from app.memory.models import MemoryCategory, MemoryEntry
from app.runtime.container import RuntimeContainer
class TestAgent(BaseAgent): pass
@pytest.mark.asyncio
async def test_event_is_delivered_and_remembered():
    runtime=RuntimeContainer();receiver=TestAgent(name='Receiver',role='Engineer',department='Engineering',description='test',goals=['observe'],responsibilities=[],capabilities=[]);sender=TestAgent(name='Sender',role='Engineer',department='Engineering',description='test',goals=[],responsibilities=[],capabilities=[])
    await receiver.initialize(runtime);await sender.initialize(runtime);event=await sender.send_message(receiver.agent_id,{'text':'hello'})
    assert event.status.value=='processed';assert event.event_id in receiver.inbox;assert len(await runtime.memory.list_memory())>=1
@pytest.mark.asyncio
async def test_registry_heartbeat_and_context():
    runtime=RuntimeContainer();agent=TestAgent(name='A',role='R',department='D',description='d',goals=['g'],responsibilities=[],capabilities=[]);await agent.initialize(runtime);await agent.heartbeat();context=await agent.load_context()
    assert (await runtime.registry.find_agent(agent.agent_id))['health']=='healthy';assert 'constitution' in context;assert agent.state==AgentState.IDLE
@pytest.mark.asyncio
async def test_memory_and_reasoning():
    runtime=RuntimeContainer();entry=await runtime.memory.create_memory(MemoryEntry(category=MemoryCategory.COMPANY,author='system',content={'text':'security first'},tags=['security'],importance=10))
    assert (await runtime.memory.search_memory('security'))[0].id==entry.id;assert (await runtime.reasoning.classify({},['a','b']))=='a'
