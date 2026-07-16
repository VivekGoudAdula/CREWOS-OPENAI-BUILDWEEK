from fastapi import APIRouter,HTTPException
from app.events.models import Event,EventType
from app.qa.models import QAStart
from app.runtime.container import runtime
router=APIRouter(prefix='/qa',tags=['Quality Assurance'])
@router.post('/start',status_code=202)
async def start(payload:QAStart):
    patch=next((item for item in runtime.engineering.patches if item.patch_id==payload.patch_id),None);repo=await runtime.engineering.get_repository(payload.repository_id)
    if not patch or not repo:raise HTTPException(404,'Patch or repository not found')
    await runtime.event_bus.publish(Event(type=EventType.SYSTEM_EVENT,source='qa-agent',payload={'action':'qa_received_patch','patch_id':patch.patch_id}));plan=await runtime.qa.plan(patch,repo);await runtime.event_bus.publish(Event(type=EventType.SYSTEM_EVENT,source='qa-agent',payload={'action':'qa_test_plan_generated','patch_id':patch.patch_id,'plan_id':plan.plan_id}));results=await runtime.qa.execute(plan,repo);report,bugs=await runtime.qa.finalize(patch,plan,results);await runtime.event_bus.publish(Event(type=EventType.SYSTEM_EVENT,source='qa-agent',targets=[patch.engineer],payload={'action':'qa_report_completed','patch_id':patch.patch_id,'report_id':report.report_id,'status':report.overall_status.value,'bug_count':len(bugs)}));return {'plan':plan,'results':results,'report':report,'bugs':bugs}
@router.get('/tests')
async def tests():return runtime.qa.results
@router.get('/reports')
async def reports():return runtime.qa.reports
@router.get('/bugs')
async def bugs():return runtime.qa.bugs
@router.get('/regression')
async def regression():return [result for result in runtime.qa.results if result.suite in ('unit','integration')]
@router.get('/acceptance')
async def acceptance():return [{'patch_id':report.patch_id,'passed':report.overall_status=='approved','recommendation':report.recommendation} for report in runtime.qa.reports]
@router.get('/approvals')
async def approvals():return [{'patch_id':report.patch_id,'status':report.overall_status,'confidence':report.release_confidence} for report in runtime.qa.reports]
