from pydantic import BaseModel, Field
class Constitution(BaseModel):
    mission:str='Ship production-quality software.'
    rules:list[str]=Field(default_factory=lambda:['Never deploy failing tests.','Security first.','Accessibility required.','CEO approval required for release.'])
class ConstitutionService:
    def __init__(self,constitution:Constitution|None=None):self._constitution=constitution or Constitution()
    async def load(self)->Constitution:return self._constitution
