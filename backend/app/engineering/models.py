from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel, Field
from app.schemas.common import utcnow
class Repository(BaseModel): repository_id:str=Field(default_factory=lambda:str(uuid4())); project_id:str|None=None; workspace:str; framework:str|None=None; language:str|None=None; branch:str|None=None; current_commit:str|None=None; preview_url:str|None=None
class RepositoryAnalysis(BaseModel): repository_id:str; tree:list[str]; dependencies:list[str]; framework:str|None=None; language:str|None=None; architecture_summary:str; implementation_strategy:str
class Patch(BaseModel): patch_id:str=Field(default_factory=lambda:str(uuid4())); task_id:str; engineer:str; changed_files:list[str]; added_files:list[str]; deleted_files:list[str]; unified_diff:str; lines_added:int; lines_removed:int; summary:str; reason:str; timestamp:object=Field(default_factory=utcnow)
class CodeReview(BaseModel): review_id:str=Field(default_factory=lambda:str(uuid4())); patch_id:str; status:str; comments:list[str]; confidence:float; timestamp:object=Field(default_factory=utcnow)
class EngineeringStart(BaseModel): repository_id:str; task_id:str; task_description:str; engineer:str
