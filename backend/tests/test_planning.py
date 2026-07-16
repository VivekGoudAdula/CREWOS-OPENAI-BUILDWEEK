import pytest
from app.events.models import Event, EventType
from app.planning.agents import CEOPlanningAgent, ProjectManagerPlanningAgent
from app.planning.models import PlanningStatus
from app.runtime.container import RuntimeContainer
def employee(cls,name,role):return cls(name=name,role=role,department='Product',description='test',goals=[],responsibilities=[],capabilities=[])
@pytest.mark.asyncio
async def test_event_driven_project_plan_is_generated():
    runtime=RuntimeContainer();ceo=employee(CEOPlanningAgent,'CEO','CEO');pm=employee(ProjectManagerPlanningAgent,'PM','Project Manager');await ceo.initialize(runtime);await pm.initialize(runtime)
    project=await runtime.projects.create('Build a streaming platform with profiles and recommendations.')
    await runtime.event_bus.publish(Event(type=EventType.PROJECT_PLANNING_REQUEST,source='test',payload={'project_id':project.project_id}))
    completed=await runtime.projects.get(project.project_id)
    assert completed.status is PlanningStatus.READY
    assert completed.strategy and completed.epics and completed.tasks and completed.timeline
    assert any(task.dependencies for task in completed.tasks)
    assert await runtime.memory.list_memory()
