from app.agents.base import AgentState, BaseAgent
from app.events.models import Event, EventType
from app.memory.models import MemoryCategory
class CEOPlanningAgent(BaseAgent):
    async def receive_event(self,event:Event)->None:
        if event.type is EventType.DECISION_REQUEST:
            decision_id=event.payload['decision_id'];options=event.payload.get('options',[]);await self.set_state(AgentState.THINKING);await self.set_state(AgentState.REASONING)
            context=await self.load_context();choice=options[0] if options else 'No decision option supplied';decision=await self._runtime.decisions.resolve(decision_id,choice=choice,reasoning=f'CEO evaluated the decision context with {len(context["relevant_memory"])} relevant memory records.',approved_by=self.agent_id,confidence=0.7);await self.update_memory(MemoryCategory.ARCHITECTURE_DECISION,{'decision':decision.model_dump(mode='json')});await self.publish_event(Event(type=EventType.DECISION_RESPONSE,source=self.agent_id,targets=decision.participants,payload={'decision_id':decision.decision_id,'topic':decision.topic,'project_id':decision.related_project,'final_decision':decision.final_decision}));await self.set_state(AgentState.IDLE);return
        if event.type is not EventType.PROJECT_PLANNING_REQUEST:return await super().receive_event(event)
        project=await self._runtime.projects.get(event.payload['project_id'])
        if not project:return
        await self.set_state(AgentState.THINKING);await self.publish_event(Event(type=EventType.CEO_STARTED,source=self.agent_id,payload={'project_id':project.project_id}))
        await self.set_state(AgentState.REASONING);strategy=await self._runtime.planning_provider.strategy(project.idea);await self._runtime.projects.strategy(project.project_id,strategy);await self.update_memory(MemoryCategory.COMPANY,{'project_id':project.project_id,'kind':'executive_strategy','strategy':strategy.model_dump(mode='json'),'goals':strategy.goals})
        await self.set_state(AgentState.COMPLETED);await self.publish_event(Event(type=EventType.CEO_COMPLETED,source=self.agent_id,payload={'project_id':project.project_id}));await self.publish_event(Event(type=EventType.CEO_STRATEGY_CREATED,source=self.agent_id,payload={'project_id':project.project_id}));await self.set_state(AgentState.IDLE)
class ProjectManagerPlanningAgent(BaseAgent):
    async def receive_event(self,event:Event)->None:
        if event.type is not EventType.CEO_STRATEGY_CREATED:return await super().receive_event(event)
        project=await self._runtime.projects.get(event.payload['project_id'])
        if not project or not project.strategy:return
        await self.set_state(AgentState.THINKING);await self.publish_event(Event(type=EventType.PM_STARTED,source=self.agent_id,payload={'project_id':project.project_id}));await self.set_state(AgentState.REASONING)
        epics,tasks,timeline=await self._runtime.planning_provider.roadmap(project.idea,project.strategy);await self._runtime.projects.roadmap(project.project_id,epics,tasks,timeline);await self.update_memory(MemoryCategory.PROJECT,{'project_id':project.project_id,'kind':'roadmap','epics':[epic.model_dump() for epic in epics],'tasks':[task.model_dump(mode='json') for task in tasks],'timeline':timeline.model_dump(mode='json'),'dependencies':[{ 'task_id':task.task_id,'dependencies':task.dependencies} for task in tasks],'milestones':[milestone.model_dump(mode='json') for milestone in timeline.sprints]})
        for task in tasks:await self.publish_event(Event(type=EventType.TASK_CREATED,source=self.agent_id,payload={'project_id':project.project_id,'task_id':task.task_id}))
        await self.publish_event(Event(type=EventType.TIMELINE_CREATED,source=self.agent_id,payload={'project_id':project.project_id}));await self.publish_event(Event(type=EventType.KANBAN_CREATED,source=self.agent_id,payload={'project_id':project.project_id}));await self.publish_event(Event(type=EventType.ROADMAP_CREATED,source=self.agent_id,payload={'project_id':project.project_id,'task_count':len(tasks)}));await self.set_state(AgentState.COMPLETED);await self.publish_event(Event(type=EventType.PROJECT_READY,source=self.agent_id,payload={'project_id':project.project_id}));await self.set_state(AgentState.IDLE)
