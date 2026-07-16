import asyncio
import subprocess
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.engineering.models import EngineeringStart
from app.runtime.container import runtime
router=APIRouter(tags=['Engineering'])
class RepositoryCreate(BaseModel): workspace:str; project_id:str|None=None
@router.post('/repository',status_code=201)
async def create_repository(payload:RepositoryCreate):
    try:return await runtime.engineering.create_repository(payload.workspace,payload.project_id)
    except ValueError as error:raise HTTPException(422,str(error))
@router.get('/repository')
async def repositories(project_id:str|None=None):
    if project_id:
        repository=await runtime.engineering.find_project_repository(project_id)
        return [repository] if repository else []
    return list(runtime.engineering.repositories.values())
@router.get('/repository/{repository_id}/tree')
async def tree(repository_id:str):
    repo=await runtime.engineering.get_repository(repository_id)
    if not repo:raise HTTPException(404,'Repository not found')
    return await runtime.engineering.tree(repo)
@router.get('/repository/{repository_id}/analysis')
async def analysis(repository_id:str):
    repo=await runtime.engineering.get_repository(repository_id)
    if not repo:raise HTTPException(404,'Repository not found')
    return await runtime.engineering.analyze(repo)
@router.get('/repository/{repository_id}/file')
async def file(repository_id:str,path:str):
    repo=await runtime.engineering.get_repository(repository_id)
    if not repo:raise HTTPException(404,'Repository not found')
    try:return {'path':path,'content':await runtime.engineering.read_file(repo,path)}
    except ValueError as error:raise HTTPException(422,str(error))
@router.get('/repository/{repository_id}/preview')
async def preview(repository_id:str):
    repo=await runtime.engineering.get_repository(repository_id)
    if not repo:raise HTTPException(404,'Repository not found')
    try:return {'url':await runtime.engineering.ensure_preview(repo)}
    except (ValueError,subprocess.SubprocessError) as error:raise HTTPException(422,str(error))
@router.get('/repository/{repository_id}/preview/{asset_path:path}',include_in_schema=False)
async def preview_asset(repository_id:str,asset_path:str=''):
    repo=await runtime.engineering.get_repository(repository_id)
    if not repo:raise HTTPException(404,'Repository not found')
    try:
        preview_root=(await runtime.engineering.build_preview(repo)).resolve()
    except (ValueError,subprocess.SubprocessError) as error:raise HTTPException(422,str(error))
    requested=(preview_root/asset_path).resolve()
    if asset_path and preview_root in requested.parents and requested.is_file():
        return FileResponse(requested)
    return FileResponse(preview_root/'index.html')
@router.post('/engineering/start',status_code=202)
async def start(payload:EngineeringStart):
    try:return await runtime.engineering.start(payload,runtime.event_bus)
    except ValueError as error:raise HTTPException(422,str(error))
@router.post('/engineering/projects/{project_id}/retry',status_code=202)
async def retry_project_generation(project_id:str):
    project=await runtime.projects.get(project_id)
    if not project:raise HTTPException(404,'Project not found')
    engineer=next((agent for agent in runtime.agents if getattr(agent,'role',None)=='Engineer'),None)
    if engineer is None or not hasattr(engineer,'_implement'):raise HTTPException(409,'Engineering runtime is unavailable')
    from app.agents.base import AgentState
    await engineer.set_state(AgentState.WORKING)
    asyncio.create_task(engineer._implement(project_id))
    return {'status':'started','project_id':project_id}
@router.get('/engineering/tasks')
async def tasks():return []
@router.get('/engineering/patches')
async def patches():return runtime.engineering.patches
@router.get('/engineering/reviews')
async def reviews():return runtime.engineering.reviews
@router.get('/engineering/feed')
async def feed():return await runtime.collaboration.activity('System Event')
