from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field
from app.schemas.common import utcnow
class PlanningStatus(str,Enum): PENDING='pending'; STRATEGIZING='strategizing'; PLANNING='planning'; READY='ready'; FAILED='failed'
class Priority(str,Enum): CRITICAL='critical'; HIGH='high'; MEDIUM='medium'; LOW='low'
class Complexity(str,Enum): SMALL='small'; MEDIUM='medium'; LARGE='large'; EXTRA_LARGE='extra_large'
class TaskStatus(str,Enum): BACKLOG='backlog'; READY='ready'; IN_PROGRESS='in_progress'; BLOCKED='blocked'; REVIEW='review'; DONE='done'
class ExecutiveStrategy(BaseModel): vision:str; goals:list[str]; scope:list[str]; success_criteria:list[str]; risks:list[str]; business_priorities:list[str]; recommended_technology_stack:list[str]; complexity:Complexity; departments:list[str]; executive_summary:str
class PlannedTask(BaseModel): task_id:str=Field(default_factory=lambda:str(uuid4())); title:str; description:str; priority:Priority; complexity:Complexity; estimated_hours:int=Field(ge=1); department:str; assigned_role:str; dependencies:list[str]=Field(default_factory=list); acceptance_criteria:list[str]; status:TaskStatus=TaskStatus.BACKLOG; created_time:object=Field(default_factory=utcnow)
class Epic(BaseModel): epic_id:str=Field(default_factory=lambda:str(uuid4())); title:str; description:str; priority:Priority; stories:list[str]=Field(default_factory=list); task_ids:list[str]=Field(default_factory=list)
class Milestone(BaseModel): milestone_id:str=Field(default_factory=lambda:str(uuid4())); title:str; sprint:int; task_ids:list[str]; estimated_hours:int
class Timeline(BaseModel): sprints:list[Milestone]; estimated_duration_weeks:int; critical_path:list[str]; delivery_forecast:str
class ProjectPlan(BaseModel): project_id:str=Field(default_factory=lambda:str(uuid4())); idea:str; name:str; status:PlanningStatus=PlanningStatus.PENDING; strategy:ExecutiveStrategy|None=None; epics:list[Epic]=Field(default_factory=list); tasks:list[PlannedTask]=Field(default_factory=list); timeline:Timeline|None=None; created_time:object=Field(default_factory=utcnow)
