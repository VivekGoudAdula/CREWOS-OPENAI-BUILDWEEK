import asyncio,time
from pathlib import Path
from app.qa.models import Bug,QAStatus,QualityReport,TestPlan,TestResult,Severity
class QAService:
    def __init__(self):self.plans=[];self.results=[];self.bugs=[];self.reports=[]
    async def plan(self,patch,repo)->TestPlan:
        tree=await __import__('app.runtime.container',fromlist=['runtime']).runtime.engineering.tree(repo);suites=[];critical=[]
        if any(path.endswith(('package.json','ts','tsx','js')) for path in tree):suites.extend(['unit','static']);critical.append('frontend')
        if any(path.endswith(('requirements.txt','py')) for path in tree):suites.extend(['integration','static']);critical.append('backend')
        if not suites:suites=['static']
        risk='high' if patch.lines_added+patch.lines_removed>300 or patch.deleted_files else 'medium'
        plan=TestPlan(patch_id=patch.patch_id,scope=patch.changed_files+patch.added_files,required_suites=list(dict.fromkeys(suites)),risk_level=risk,critical_areas=critical,estimated_execution_seconds=len(suites)*60,priority='high' if risk=='high' else 'medium');self.plans.append(plan);return plan
    async def _run(self,patch_id,suite,command,cwd)->TestResult:
        started=time.perf_counter()
        try:
            process=await asyncio.create_subprocess_exec(*command,cwd=cwd,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT);out,_=await process.communicate();passed=process.returncode==0;output=out.decode('utf-8',errors='replace')[-10000:]
        except OSError as error:passed=False;output=str(error)
        return TestResult(patch_id=patch_id,suite=suite,command=command,passed=passed,output=output,duration_ms=int((time.perf_counter()-started)*1000))
    async def execute(self,plan,repo)->list[TestResult]:
        root=Path(repo.workspace);commands=[]
        if 'unit' in plan.required_suites and (root/'frontend'/'package.json').exists():commands.append(('unit',['npm.cmd','test'],str(root/'frontend')))
        if 'integration' in plan.required_suites and (root/'backend'/'tests').exists():commands.append(('integration',['python','-m','pytest','tests','-q'],str(root/'backend')))
        commands.append(('static',['python','-c','import ast,pathlib; [ast.parse(p.read_text(encoding="utf-8")) for p in pathlib.Path(".").rglob("*.py")]; print("syntax ok")'],str(root/'backend') if (root/'backend').exists() else str(root)))
        results=[await self._run(plan.patch_id,suite,command,cwd) for suite,command,cwd in commands];self.results.extend(results);return results
    async def finalize(self,patch,plan,results)->tuple[QualityReport,list[Bug]]:
        failures=[result for result in results if not result.passed];bugs=[]
        for failure in failures:bugs.append(Bug(title=f'{failure.suite.title()} validation failed',description=failure.output[-1000:],severity=Severity.HIGH if plan.risk_level=='high' else Severity.MEDIUM,priority='high',affected_files=plan.scope,affected_patch=patch.patch_id,assigned_engineer=patch.engineer,steps_to_reproduce=['Run: '+' '.join(failure.command)],expected_result='Command exits with code 0.',actual_result=f'Command exited unsuccessfully after {failure.duration_ms}ms.'))
        self.bugs.extend(bugs);total=len(results);passed=total-len(failures);confidence=round(passed/total,2) if total else 0.0;status=QAStatus.APPROVED if not failures else QAStatus.NEEDS_CHANGES
        report=QualityReport(patch_id=patch.patch_id,tests_executed=total,tests_passed=passed,tests_failed=len(failures),readability_score=round(0.8 if not failures else 0.55,2),maintainability_score=round(0.8 if not failures else 0.55,2),risk_score=0.3 if plan.risk_level=='medium' else 0.6,release_confidence=confidence,overall_status=status,recommendation='Patch is approved based on executed validations.' if not failures else 'Patch requires changes; see generated bugs.');self.reports.append(report);return report,bugs
