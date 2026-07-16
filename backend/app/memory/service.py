from collections.abc import Iterable
from app.memory.models import MemoryCategory, MemoryEntry
class MemoryService:
    """Central asynchronous memory store. A Mongo adapter can replace this service without changing agents."""
    def __init__(self): self._entries: dict[str, MemoryEntry] = {};self._collection=None
    def set_database(self,database)->None:self._collection=database['company_memory']
    async def _persist(self,entry:MemoryEntry)->None:
        if self._collection is not None:await self._collection.replace_one({'id':entry.id},entry.model_dump(mode='json'),upsert=True)
    async def create_memory(self, entry: MemoryEntry) -> MemoryEntry: self._entries[entry.id]=entry;await self._persist(entry);return entry
    async def update_memory(self, memory_id:str, **changes) -> MemoryEntry | None:
        entry=self._entries.get(memory_id)
        if not entry:return None
        self._entries[memory_id]=entry.model_copy(update=changes); await self._persist(self._entries[memory_id]);return self._entries[memory_id]
    async def delete_memory(self,memory_id:str)->bool:
        deleted=self._entries.pop(memory_id,None) is not None
        if self._collection is not None:await self._collection.delete_one({'id':memory_id})
        return deleted
    async def search_memory(self, query:str='', *, categories:Iterable[MemoryCategory]|None=None, tags:Iterable[str]|None=None, limit:int=50)->list[MemoryEntry]:
        categories=set(categories or []); tags=set(tags or []); needle=query.lower()
        result=[m for m in self._entries.values() if (not categories or m.category in categories) and (not tags or tags.intersection(m.tags)) and (not needle or needle in str(m.content).lower())]
        return sorted(result,key=lambda m:(m.importance,str(m.timestamp)),reverse=True)[:limit]
    async def retrieve_context(self, agent_id:str, *, limit:int=20)->list[MemoryEntry]:
        return await self.search_memory(categories=[MemoryCategory.COMPANY,MemoryCategory.AGENT,MemoryCategory.PROJECT,MemoryCategory.LONG_TERM],limit=limit)
    async def list_memory(self,limit:int=100)->list[MemoryEntry]:
        if self._collection is not None:
            documents=await self._collection.find({},{'_id':0}).to_list(limit)
            for document in documents:self._entries[document['id']]=MemoryEntry.model_validate(document)
        return await self.search_memory(limit=limit)
