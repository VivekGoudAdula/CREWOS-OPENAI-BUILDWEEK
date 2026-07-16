from abc import ABC, abstractmethod
from typing import Any
class ReasoningProvider(ABC):
    @abstractmethod
    async def reason(self, context:dict[str,Any])->dict[str,Any]: ...
    @abstractmethod
    async def evaluate(self, subject:dict[str,Any], criteria:dict[str,Any])->dict[str,Any]: ...
    @abstractmethod
    async def prioritize(self, items:list[dict[str,Any]])->list[dict[str,Any]]: ...
    @abstractmethod
    async def classify(self, content:dict[str,Any], labels:list[str])->str: ...
    @abstractmethod
    async def summarize(self, content:dict[str,Any])->str: ...
class DeterministicReasoningProvider(ReasoningProvider):
    """Safe local provider for runtime tests; replace through dependency injection in production."""
    async def reason(self,context):return {'outcome':'context_assessed','context_keys':list(context.keys())}
    async def evaluate(self,subject,criteria):return {'accepted':True,'criteria':criteria}
    async def prioritize(self,items):return sorted(items,key=lambda item:item.get('priority',0),reverse=True)
    async def classify(self,content,labels):return labels[0] if labels else 'unclassified'
    async def summarize(self,content):return str(content)[:500]
