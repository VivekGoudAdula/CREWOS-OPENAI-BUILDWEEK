import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.events.models import Event, EventType
from app.runtime.container import runtime
router=APIRouter(prefix='/projects',tags=['Project Planning'])
class PlanRequest(BaseModel): idea:str=Field(min_length=10,max_length=5000)
async def project_or_404(project_id:str):
    project=await runtime.projects.get(project_id)
    if not project:raise HTTPException(404,'Project not found')
    return project
@router.post('/plan',status_code=202)
async def plan(payload:PlanRequest):
    project=await runtime.projects.create(payload.idea)
    async def begin_planning():
        await runtime.event_bus.publish(Event(type=EventType.PROJECT_CREATED,source='planning-console',payload={'project_id':project.project_id,'idea':payload.idea}))
        await runtime.event_bus.publish(Event(type=EventType.PROJECT_PLANNING_REQUEST,source='planning-console',payload={'project_id':project.project_id,'idea':payload.idea}))
    asyncio.create_task(begin_planning())
    return project
@router.get('')
async def projects():return await runtime.projects.list()
@router.get('/{project_id}')
async def project(project_id:str):return await project_or_404(project_id)
@router.get('/{project_id}/roadmap')
async def roadmap(project_id:str):
    project=await project_or_404(project_id);return {'strategy':project.strategy,'epics':project.epics,'milestones':project.timeline.sprints if project.timeline else []}
@router.get('/{project_id}/tasks')
async def tasks(project_id:str):return (await project_or_404(project_id)).tasks
@router.get('/{project_id}/timeline')
async def timeline(project_id:str):return (await project_or_404(project_id)).timeline
@router.get('/{project_id}/dependencies')
async def dependencies(project_id:str):return [{'task_id':task.task_id,'depends_on':task.dependencies} for task in (await project_or_404(project_id)).tasks]
@router.get('/{project_id}/kanban')
async def kanban(project_id:str):
    project=await project_or_404(project_id);return {status.value:[task for task in project.tasks if task.status==status] for status in __import__('app.planning.models',fromlist=['TaskStatus']).TaskStatus}
