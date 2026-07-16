"""Runtime participants used to validate the reusable autonomous substrate.

They do not plan projects or execute product work; they only exercise the runtime lifecycle.
"""
from app.agents.base import BaseAgent
from app.events.models import Event, EventType
from app.runtime.container import RuntimeContainer
from app.planning.agents import CEOPlanningAgent, ProjectManagerPlanningAgent
from app.engineering.agent import EngineeringRuntimeAgent
class RuntimeEmployee(BaseAgent):
    pass
async def bootstrap_runtime(runtime:RuntimeContainer)->list[RuntimeEmployee]:
    employees=[
        RuntimeEmployee(name='Runtime Observer',role='Runtime Observer',department='Platform',description='Observes runtime health and shared context.',goals=['Maintain runtime awareness'],responsibilities=['Observe system events'],capabilities=['event-observation','context-awareness']),
        RuntimeEmployee(name='Knowledge Steward',role='Knowledge Steward',department='Platform',description='Maintains shared organizational memory.',goals=['Maintain reliable shared memory'],responsibilities=['Record runtime knowledge'],capabilities=['memory-management','event-observation']),
    ]
    planning_agents=[CEOPlanningAgent(name='Chief Executive Officer',role='CEO',department='Executive',description='Creates product strategy.',goals=['Create an approved business strategy'],responsibilities=['Vision and scope'],capabilities=['strategy','prioritization']),ProjectManagerPlanningAgent(name='Project Manager',role='Project Manager',department='Product',description='Converts strategy into execution plans.',goals=['Create executable roadmaps'],responsibilities=['Epics, tasks and timelines'],capabilities=['planning','dependency-analysis']),RuntimeEmployee(name='Product Designer',role='Designer',department='Design',description='Reviews product experience scope.',goals=['Maintain usable product scope'],responsibilities=['Experience review'],capabilities=['ux-review','accessibility']),EngineeringRuntimeAgent(name='Software Engineer',role='Engineer',department='Engineering',description='Builds project workspaces from approved plans.',goals=['Produce implementation-ready source code'],responsibilities=['Repository analysis and code generation'],capabilities=['architecture-review','code-generation','patch-review']),RuntimeEmployee(name='Quality Advocate',role='QA',department='Quality',description='Reviews acceptance and quality risks.',goals=['Maintain quality visibility'],responsibilities=['Quality review'],capabilities=['acceptance-review','risk-identification'])]
    employees.extend(planning_agents)
    for employee in employees: await employee.initialize(runtime)
    await runtime.event_bus.publish(Event(type=EventType.SYSTEM_EVENT,source='runtime-bootstrap',payload={'message':'CrewOS runtime initialized','participants':[employee.agent_id for employee in employees]}))
    return employees
