from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel, Field
from app.config.settings import get_settings
class GeneratedFile(BaseModel): path:str; content:str
class GenerationResult(BaseModel): implementation_plan:list[str]; files:list[GeneratedFile]=Field(default_factory=list); summary:str
class CodeGenerationProvider(ABC):
    @abstractmethod
    async def generate(self,*,task_description:str,repository_context:str)->GenerationResult: ...
class AzureOpenAICodeGenerationProvider(CodeGenerationProvider):
    """Azure OpenAI provider. It returns a structured plan/files payload; workspace writes remain controlled by EngineeringService."""
    def _client(self):
        settings=get_settings()
        if not all([settings.azure_openai_endpoint,settings.azure_openai_api_key,settings.azure_api_version,settings.azure_gpt_deployment]):
            raise RuntimeError('Azure OpenAI is not configured. Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_API_VERSION, and AZURE_GPT_DEPLOYMENT.')
        from openai import AsyncAzureOpenAI
        return AsyncAzureOpenAI(azure_endpoint=settings.azure_openai_endpoint,api_key=settings.azure_openai_api_key,api_version=settings.azure_api_version),settings.azure_gpt_deployment
    async def generate(self,*,task_description:str,repository_context:str)->GenerationResult:
        client,deployment=self._client()
        response=await client.chat.completions.create(model=deployment,response_format={'type':'json_object'},messages=[{'role':'system','content':'You are a principal frontend and backend engineer with exceptional product-design judgment. Return JSON only with implementation_plan (array of strings), files (array of {path, content}), and summary. Build a complete, runnable, visually polished product prototype—not a bare heading or a generic scaffold. Infer the product domain from the task and make the UI specific to it. For every React/Vite frontend, include package.json, index.html with the module entry, src/main.jsx or src/main.tsx, an app shell, reusable components, and one or more CSS files imported by the app. Use a high-quality responsive layout, strong type hierarchy, intentional color palette, gradients, cards, visual depth, hover/focus states, and restrained CSS transitions. Include realistic domain-relevant interface content, empty/loading states where useful, and accessible semantic markup. Do not depend on unavailable image assets or external UI kits; use CSS, inline SVG, and generated text/data instead. Preserve and improve existing architecture when it is present. Only write files directly needed for the task and respect the repository context.'},{'role':'user','content':f'Task:\n{task_description}\n\nRepository context:\n{repository_context}'}])
        return GenerationResult.model_validate_json(response.choices[0].message.content or '{}')
