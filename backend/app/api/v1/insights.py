import io,json,zipfile
from datetime import datetime
from fastapi import APIRouter,HTTPException
from fastapi.responses import Response
from app.runtime.container import runtime
router=APIRouter(tags=['Mission Control'])
async def snapshot():
    agents=await runtime.registry.list_agents();projects=await runtime.projects.list();activity=await runtime.collaboration.activity();reports=runtime.qa.reports;bugs=runtime.qa.bugs;decisions=await runtime.decisions.list()
    return {'generated_at':datetime.utcnow().isoformat()+'Z','projects':projects,'agents':agents,'activity':activity,'quality_reports':reports,'bugs':bugs,'decisions':decisions,'messages':await runtime.collaboration.messages(),'meetings':runtime.collaboration._meetings}
@router.get('/dashboard')
async def dashboard():
    data=await snapshot();projects=data['projects'];ready=[p for p in projects if p.status.value=='ready'];reports=data['quality_reports'];latest=reports[-1] if reports else None
    return {'company_health':'healthy' if not data['bugs'] else 'attention_required','delivery_confidence':latest.release_confidence if latest else 0,'active_agents':len(data['agents']),'open_decisions':sum(d.status.value=='requested' for d in data['decisions']),'open_bugs':sum(b.status!='closed' for b in data['bugs']),'current_sprint':max((len(p.timeline.sprints) for p in projects if p.timeline),default=0),'engineering_progress':len(runtime.engineering.patches),'quality_score':latest.release_confidence if latest else 0,'release_readiness':latest.overall_status.value if latest else 'not_validated','recent_activity':data['activity'][:20]}
@router.get('/analytics')
async def analytics():
    data=await snapshot();return {'projects_completed':sum(p.status.value=='ready' for p in data['projects']),'tasks_completed':sum(sum(t.status.value=='done' for t in p.tasks) for p in data['projects']),'agent_productivity':{a['name']:len([x for x in data['activity'] if x.agent==a['agent_id']]) for a in data['agents']},'bugs_detected':len(data['bugs']),'approval_rate':(sum(r.overall_status.value=='approved' for r in data['quality_reports'])/len(data['quality_reports']) if data['quality_reports'] else 0),'events_processed':len(await runtime.event_bus.history()),'messages_sent':len(data['messages']),'decision_count':len(data['decisions']),'department_workload':{department:len([a for a in data['agents'] if a['department']==department]) for department in {a['department'] for a in data['agents']}}}
@router.get('/history')
async def history():
    data=await snapshot();return [{'project':p,'decisions':[d for d in data['decisions'] if d.related_project==p.project_id],'qa_reports':[r for r in data['quality_reports'] if r.patch_id]} for p in data['projects']]
@router.get('/performance')
async def performance():return {'events_in_memory':len(await runtime.event_bus.history()),'active_websocket_channels':{name:len(sockets) for name,sockets in runtime.hub._channels.items()},'agent_throughput':sum(len(agent.inbox) for agent in runtime.agents),'queue_length':sum(len(agent.inbox) for agent in runtime.agents),'note':'Process CPU and memory require a host metrics collector and are intentionally not invented.'}
@router.get('/summary')
async def summary():
    data=await snapshot();return {'vision':[p.strategy.vision for p in data['projects'] if p.strategy],'engineering_summary':f'{len(runtime.engineering.patches)} patches recorded.','qa_summary':f'{len(data["quality_reports"])} QA reports and {len(data["bugs"])} bugs recorded.','timeline':f'{len(data["projects"])} projects in history.','risk':'Open bugs require review.' if data['bugs'] else 'No recorded open bugs.','final_status':'ready' if data['projects'] else 'awaiting_project'}
@router.get('/exports')
async def exports(format:str='json'):
    data=await snapshot();payload=json.dumps(data,default=str,indent=2)
    if format=='json':return Response(payload,media_type='application/json',headers={'Content-Disposition':'attachment; filename=crewos-summary.json'})
    if format=='markdown':return Response('# CrewOS Project Summary\n\n```json\n'+payload+'\n```',media_type='text/markdown',headers={'Content-Disposition':'attachment; filename=crewos-summary.md'})
    if format=='zip':
        buffer=io.BytesIO();
        with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:archive.writestr('crewos-summary.json',payload)
        return Response(buffer.getvalue(),media_type='application/zip',headers={'Content-Disposition':'attachment; filename=crewos-summary.zip'})
    raise HTTPException(422,'Supported formats: json, markdown, zip')
