from app.decisions.models import Conflict, Decision, DecisionStatus
class DecisionService:
    def __init__(self):self._decisions:dict[str,Decision]={};self._conflicts:dict[str,Conflict]={};self._db=None
    def set_database(self,database)->None:self._db=database
    async def _store(self,collection,key,value):
        if self._db is not None:await self._db[collection].replace_one({key:getattr(value,key)},value.model_dump(mode='json'),upsert=True)
    async def create_from_conflict(self,conflict:Conflict)->Decision:
        self._conflicts[conflict.conflict_id]=conflict;await self._store('conflicts','conflict_id',conflict);decision=Decision(topic=conflict.topic,context=conflict.context,participants=conflict.participants,options_considered=list(conflict.positions.values()),created_by='conflict-engine',related_project=conflict.related_project);self._decisions[decision.decision_id]=decision;await self._store('decisions','decision_id',decision);return decision
    async def resolve(self,decision_id:str,*,choice:str,reasoning:str,approved_by:str,confidence:float)->Decision:
        decision=self._decisions[decision_id];decision.final_decision=choice;decision.reasoning=reasoning;decision.approved_by=approved_by;decision.confidence=confidence;decision.status=DecisionStatus.APPROVED;await self._store('decisions','decision_id',decision);return decision
    async def list(self,query:str|None=None)->list[Decision]:return [d for d in self._decisions.values() if not query or query.lower() in f'{d.topic} {d.context} {d.final_decision}'.lower()]
    async def get(self,decision_id:str)->Decision|None:return self._decisions.get(decision_id)
