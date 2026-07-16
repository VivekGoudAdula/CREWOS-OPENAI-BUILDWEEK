from app.planning.models import PlanningStatus, ProjectPlan
class ProjectPlanningService:
    def __init__(self):self._projects:dict[str,ProjectPlan]={};self._collection=None
    def set_database(self,database)->None:self._collection=database['projects']
    async def _persist(self,project:ProjectPlan)->None:
        if self._collection is not None:await self._collection.replace_one({'project_id':project.project_id},project.model_dump(mode='json'),upsert=True)
    async def create(self,idea:str)->ProjectPlan:
        name=' '.join(idea.strip().split()[:8]);project=ProjectPlan(idea=idea,name=name,status=PlanningStatus.STRATEGIZING);self._projects[project.project_id]=project;await self._persist(project);return project
    async def get(self,project_id:str)->ProjectPlan|None:
        if project_id in self._projects:return self._projects[project_id]
        if self._collection is not None:
            document=await self._collection.find_one({'project_id':project_id},{'_id':0})
            if document: self._projects[project_id]=ProjectPlan.model_validate(document);return self._projects[project_id]
        return None
    async def list(self)->list[ProjectPlan]:
        if self._collection is not None:
            documents=await self._collection.find({},{'_id':0}).to_list(500)
            for document in documents:self._projects[document['project_id']]=ProjectPlan.model_validate(document)
        return list(self._projects.values())
    async def strategy(self,project_id:str,strategy)->ProjectPlan:
        project=self._projects[project_id];project.strategy=strategy;project.status=PlanningStatus.PLANNING;await self._persist(project);return project
    async def roadmap(self,project_id:str,epics,tasks,timeline)->ProjectPlan:
        project=self._projects[project_id];project.epics=epics;project.tasks=tasks;project.timeline=timeline;project.status=PlanningStatus.READY;await self._persist(project);return project
