from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field
from app.schemas.common import utcnow
class QAStatus(str,Enum): APPROVED='approved'; APPROVED_WITH_SUGGESTIONS='approved_with_suggestions'; NEEDS_CHANGES='needs_changes'; REJECTED='rejected'
class Severity(str,Enum): CRITICAL='critical'; HIGH='high'; MEDIUM='medium'; LOW='low'; SUGGESTION='suggestion'
class TestPlan(BaseModel): plan_id:str=Field(default_factory=lambda:str(uuid4())); patch_id:str; scope:list[str]; required_suites:list[str]; risk_level:str; critical_areas:list[str]; estimated_execution_seconds:int; priority:str; timestamp:object=Field(default_factory=utcnow)
class TestResult(BaseModel): result_id:str=Field(default_factory=lambda:str(uuid4())); patch_id:str; suite:str; command:list[str]; passed:bool; output:str; duration_ms:int; timestamp:object=Field(default_factory=utcnow)
class Bug(BaseModel): bug_id:str=Field(default_factory=lambda:str(uuid4())); title:str; description:str; severity:Severity; priority:str; status:str='open'; affected_files:list[str]; affected_patch:str; assigned_engineer:str; steps_to_reproduce:list[str]; expected_result:str; actual_result:str; timestamp:object=Field(default_factory=utcnow)
class QualityReport(BaseModel): report_id:str=Field(default_factory=lambda:str(uuid4())); patch_id:str; tests_executed:int; tests_passed:int; tests_failed:int; test_coverage:float|None=None; readability_score:float; maintainability_score:float; risk_score:float; release_confidence:float; overall_status:QAStatus; recommendation:str; timestamp:object=Field(default_factory=utcnow)
class QAStart(BaseModel): patch_id:str; repository_id:str
