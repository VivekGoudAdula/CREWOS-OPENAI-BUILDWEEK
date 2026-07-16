from typing import Any
from app.planning.models import Complexity, ExecutiveStrategy, Epic, Milestone, PlannedTask, Priority, TaskStatus, Timeline
from app.schemas.common import utcnow
class PlanningProvider:
    """Planning contract: an LLM-backed provider can replace this implementation without changing agents."""
    async def strategy(self, idea:str)->ExecutiveStrategy: raise NotImplementedError
    async def roadmap(self, idea:str, strategy:ExecutiveStrategy)->tuple[list[Epic],list[PlannedTask],Timeline]: raise NotImplementedError
class DeterministicPlanningProvider(PlanningProvider):
    capability_signals={
        'stream|video|movie|series': ['Account Access','Content Library','Video Playback','Discovery and Recommendations','Subscription Management','Watchlist and History','Content Administration'],
        'expense|receipt|budget|finance': ['Account Access','Transaction Capture','Receipt Processing','Budget Management','Financial Dashboard','Analytics and Reports','Settings'],
        'delivery|restaurant|order|menu': ['Account Access','Merchant Catalog','Order Management','Delivery Tracking','Payments','Customer Notifications','Operations Console'],
        'crm|customer|lead|sales': ['Account Access','Contact Management','Pipeline Management','Activity Tracking','Analytics and Reports','Administration'],
    }
    def _concepts(self,idea:str)->list[str]:
        terms=[' '.join(part.split()[:5]).strip(' .') for part in idea.replace(' and ', ',').replace(' with ', ',').split(',')]
        return list(dict.fromkeys(term.title() for term in terms if len(term)>2))[:5] or ['Product Foundation']
    def _capabilities(self,idea:str)->list[str]:
        import re
        normalized=idea.lower();found=[]
        for pattern,capabilities in self.capability_signals.items():
            if re.search(pattern,normalized):found.extend(capabilities)
        return list(dict.fromkeys(found or self._concepts(idea)))
    async def strategy(self,idea:str)->ExecutiveStrategy:
        concepts=self._capabilities(idea); complexity=Complexity.EXTRA_LARGE if len(concepts)>6 else Complexity.LARGE if len(concepts)>3 else Complexity.MEDIUM
        return ExecutiveStrategy(vision=f'Deliver a reliable product that fulfills: {idea.strip()}',goals=[f'Provide a measurable {concept.lower()} outcome' for concept in concepts],scope=concepts,success_criteria=[f'{concept} is usable, secure, and measurable' for concept in concepts],risks=['Unvalidated assumptions','Scope expansion','Security and privacy requirements'],business_priorities=concepts,recommended_technology_stack=['React','FastAPI','MongoDB','Redis'],complexity=complexity,departments=['Product','Engineering','Design','Security'],executive_summary=f'An execution plan for {idea.strip()} with {len(concepts)} distinct capability areas.')
    async def roadmap(self,idea:str,strategy:ExecutiveStrategy)->tuple[list[Epic],list[PlannedTask],Timeline]:
        epics=[];tasks=[];previous_id=None
        for index,concept in enumerate(strategy.business_priorities,1):
            epic=Epic(title=concept,description=f'Outcome area derived from the product vision: {concept}',priority=Priority.HIGH if index==1 else Priority.MEDIUM,stories=[f'Deliver validated {concept} capabilities'])
            discovery=PlannedTask(title=f'Define {concept} requirements',description=f'Capture measurable requirements and constraints for {concept}.',priority=Priority.HIGH,complexity=Complexity.SMALL,estimated_hours=8,department='Product',assigned_role='Product Manager',dependencies=[previous_id] if previous_id else [],acceptance_criteria=[f'Requirements for {concept} are approved'])
            delivery=PlannedTask(title=f'Design {concept} solution',description=f'Create an implementation-ready solution design for {concept}.',priority=Priority.HIGH,complexity=Complexity.MEDIUM,estimated_hours=16,department='Engineering',assigned_role='Software Architect',dependencies=[discovery.task_id],acceptance_criteria=[f'{concept} design addresses approved requirements'])
            epic.task_ids=[discovery.task_id,delivery.task_id];epics.append(epic);tasks.extend([discovery,delivery]);previous_id=delivery.task_id
        buckets=[tasks[i:i+2] for i in range(0,len(tasks),2)];milestones=[Milestone(title=f'Sprint {i}',sprint=i,task_ids=[t.task_id for t in bucket],estimated_hours=sum(t.estimated_hours for t in bucket)) for i,bucket in enumerate(buckets,1)]
        for milestone in milestones:
            for task in tasks:
                if task.task_id in milestone.task_ids and not task.dependencies: task.status=TaskStatus.READY
        duration=max(1,len(milestones));return epics,tasks,Timeline(sprints=milestones,estimated_duration_weeks=duration*2,critical_path=[task.task_id for task in tasks if task.dependencies],delivery_forecast=f'Estimated delivery after {duration*2} weeks of planned execution.')
