from datetime import datetime
from app.schemas.common import utcnow
class AgentRegistry:
    def __init__(self):self._agents:dict[str,dict]={}
    async def register_agent(self, agent:object)->dict:
        record={'agent_id':agent.agent_id,'name':agent.name,'role':agent.role,'department':agent.department,'capabilities':agent.capabilities,'status':agent.status.value,'health':'healthy','current_workload':0,'active_tasks':[],'last_heartbeat':utcnow()}; self._agents[agent.agent_id]=record; return record
    async def remove_agent(self,agent_id:str)->bool:return self._agents.pop(agent_id,None) is not None
    async def find_agent(self,agent_id:str)->dict|None:return self._agents.get(agent_id)
    async def find_department(self,department:str)->list[dict]:return [a for a in self._agents.values() if a['department']==department]
    async def list_agents(self)->list[dict]:return list(self._agents.values())
    async def heartbeat(self,agent_id:str,status:str,health:str='healthy')->None:
        if record:=self._agents.get(agent_id): record.update(status=status,health=health,last_heartbeat=utcnow())
    async def health_check(self)->dict:return {'registered_agents':len(self._agents),'healthy_agents':sum(a['health']=='healthy' for a in self._agents.values())}
