"""Event-driven engineering handoff for approved project plans."""
import asyncio
from pathlib import Path
from app.agents.base import AgentState, BaseAgent
from app.engineering.models import EngineeringStart
from app.events.models import Event, EventType

class EngineeringRuntimeAgent(BaseAgent):
    async def receive_event(self,event:Event)->None:
        if event.type is not EventType.PROJECT_READY:
            return await super().receive_event(event)
        project=await self._runtime.projects.get(event.payload.get('project_id',''))
        if not project:return
        await self.set_state(AgentState.WORKING)
        # The work runs independently so the planning event remains responsive.
        asyncio.create_task(self._implement(project.project_id))

    async def _implement(self,project_id:str)->None:
        try:
            project=await self._runtime.projects.get(project_id)
            if not project:return
            workspace=Path.cwd()/'project_workspaces'/project_id
            workspace.mkdir(parents=True,exist_ok=True)
            repository=await self._runtime.engineering.find_project_repository(project_id)
            if repository is None:
                repository=await self._runtime.engineering.create_repository(str(workspace),project_id)
            task_description=(
                f'Build a runnable initial prototype for this product: {project.idea}\n\n'
                f'Vision: {project.strategy.vision if project.strategy else project.idea}\n\n'
                'Required capability areas:\n- ' + '\n- '.join(epic.title for epic in project.epics) + '\n\n'
                'Create only real source files required for a coherent React/Vite frontend and FastAPI backend. '
                'The frontend must be a visually polished, demo-ready interface tailored to this exact product: use a clear visual system, gradients, responsive layouts, reusable components, and restrained CSS micro-interactions. '
                'Do not return a bare heading, placeholder screen, or unstyled scaffold. Include a README explaining how to run the generated workspace.'
            )
            result=await self._runtime.engineering.start(EngineeringStart(repository_id=repository.repository_id,task_id=f'project-{project_id}',task_description=task_description,engineer=self.agent_id),self._runtime.event_bus)
            await self.publish_event(Event(type=EventType.SYSTEM_EVENT,source=self.agent_id,payload={'action':'engineering_workspace_ready','project_id':project_id,'repository_id':repository.repository_id,'patch_id':result['patch'].patch_id,'files_changed':len(result['patch'].changed_files)+len(result['patch'].added_files)}))
            await self.set_state(AgentState.COMPLETED)
        except Exception as error:
            await self.publish_event(Event(type=EventType.SYSTEM_EVENT,source=self.agent_id,payload={'action':'engineering_workspace_failed','project_id':project_id,'error':str(error)}))
            await self.set_state(AgentState.BLOCKED)
        finally:
            if self.state is not AgentState.BLOCKED:await self.set_state(AgentState.IDLE)
