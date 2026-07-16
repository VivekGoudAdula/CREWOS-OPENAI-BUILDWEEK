import asyncio
import socket
import subprocess
import sys
import uuid
import difflib
from pathlib import Path
from app.engineering.models import CodeReview, Patch, Repository, RepositoryAnalysis
class EngineeringService:
    def __init__(self,provider):self.repositories={};self.patches=[];self.reviews=[];self.provider=provider;self._preview_processes={}
    async def create_repository(self,workspace:str,project_id:str|None=None)->Repository:
        path=Path(workspace).resolve()
        if not path.exists() or not path.is_dir():raise ValueError('Workspace must be an existing directory')
        # Project workspaces need a stable identifier across development reloads.
        repo=Repository(repository_id=f'project-{project_id}',workspace=str(path),project_id=project_id) if project_id else Repository(workspace=str(path));self.repositories[repo.repository_id]=repo;return repo
    async def get_repository(self,repository_id:str)->Repository|None:return self.repositories.get(repository_id)
    async def find_project_repository(self,project_id:str)->Repository|None:
        repository=next((repo for repo in self.repositories.values() if repo.project_id==project_id),None)
        if repository:return repository
        # The source workspace is durable even when Uvicorn reloads and clears
        # in-memory metadata. Rehydrate its repository record on demand.
        workspace=(Path.cwd()/'project_workspaces'/project_id).resolve()
        if workspace.is_dir():
            repository=Repository(repository_id=f'project-{project_id}',workspace=str(workspace),project_id=project_id)
            self.repositories[repository.repository_id]=repository
            return repository
        return None
    async def read_file(self,repo:Repository,relative_path:str)->str:
        root=Path(repo.workspace).resolve();target=(root/relative_path).resolve()
        if root not in target.parents or not target.is_file():raise ValueError('File is not available in this repository')
        return target.read_text(encoding='utf-8')
    def _frontend_root(self,repo:Repository)->Path|None:
        root=Path(repo.workspace);candidate=root/'frontend';return candidate if (candidate/'package.json').is_file() else (root if (root/'package.json').is_file() else None)
    def _preview_port(self,repo:Repository)->int:
        if repo.project_id:
            return 4500+(uuid.UUID(repo.project_id).int % 400)
        for port in range(4500,4900):
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as probe:
                if probe.connect_ex(('127.0.0.1',port))!=0:return port
        raise ValueError('No local preview port is available')
    async def ensure_preview(self,repo:Repository)->str|None:
        frontend=self._frontend_root(repo)
        if frontend is None:return None
        process=self._preview_processes.get(repo.repository_id)
        if process and process.poll() is None:return repo.preview_url
        port=self._preview_port(repo);npm='npm.cmd' if sys.platform=='win32' else 'npm'
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as probe:
            if probe.connect_ex(('127.0.0.1',port))==0:raise ValueError('This project preview port is already occupied')
        if not (frontend/'node_modules').is_dir():
            await asyncio.to_thread(subprocess.run,[npm,'install'],cwd=frontend,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
        startupinfo=None
        if sys.platform=='win32':startupinfo=subprocess.STARTUPINFO();startupinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW
        process=subprocess.Popen([npm,'run','dev','--','--port',str(port),'--host','127.0.0.1','--strictPort'],cwd=frontend,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,startupinfo=startupinfo)
        self._preview_processes[repo.repository_id]=process;repo.preview_url=f'http://127.0.0.1:{port}';return repo.preview_url
    async def tree(self,repo:Repository)->list[str]:return [str(p.relative_to(repo.workspace)) for p in Path(repo.workspace).rglob('*') if '.git' not in p.parts and 'node_modules' not in p.parts and p.is_file()][:2000]
    async def analyze(self,repo:Repository)->RepositoryAnalysis:
        tree=await self.tree(repo);deps=[];framework=language=None
        if 'frontend/package.json' in tree:
            framework='React/Vite';language='TypeScript';deps.append('frontend/package.json')
        if 'backend/requirements.txt' in tree:
            language=(language or '')+' Python';deps.append('backend/requirements.txt')
        return RepositoryAnalysis(repository_id=repo.repository_id,tree=tree,dependencies=deps,framework=framework,language=language,architecture_summary='Repository analysis derived from current structure and dependency manifests.',implementation_strategy='Analyze impacted files, produce a constrained implementation plan, apply changes through Codex, then capture and review the resulting diff.')
    async def start(self,request, event_bus):
        repo=await self.get_repository(request.repository_id)
        if not repo:raise ValueError('Repository not found')
        analysis=await self.analyze(repo)
        from app.events.models import Event, EventType
        await event_bus.publish(Event(type=EventType.SYSTEM_EVENT,source=request.engineer,payload={'action':'engineering_analysis_started','task_id':request.task_id,'repository_id':repo.repository_id}))
        generated=await self.provider.generate(task_description=request.task_description,repository_context='\n'.join(analysis.tree[:500]))
        changed=[];added=[];diffs=[];added_lines=removed_lines=0
        root=Path(repo.workspace).resolve()
        for generated_file in generated.files:
            destination=(root/generated_file.path).resolve()
            if root not in destination.parents and destination!=root:raise ValueError('Generated file path escapes repository workspace')
            old=destination.read_text(encoding='utf-8') if destination.exists() else ''
            destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(generated_file.content,encoding='utf-8')
            relative=str(destination.relative_to(root));(changed if old else added).append(relative);diff=list(difflib.unified_diff(old.splitlines(),generated_file.content.splitlines(),fromfile=f'a/{relative}',tofile=f'b/{relative}',lineterm=''));diffs.extend(diff);added_lines+=sum(line.startswith('+') and not line.startswith('+++') for line in diff);removed_lines+=sum(line.startswith('-') and not line.startswith('---') for line in diff)
        from app.engineering.models import Patch,CodeReview
        patch=Patch(task_id=request.task_id,engineer=request.engineer,changed_files=changed,added_files=added,deleted_files=[],unified_diff='\n'.join(diffs),lines_added=added_lines,lines_removed=removed_lines,summary=generated.summary,reason=request.task_description);self.patches.append(patch)
        review=CodeReview(patch_id=patch.patch_id,status='approved' if generated.files else 'needs_changes',comments=[] if generated.files else ['Provider returned no files.'],confidence=0.65);self.reviews.append(review)
        await self.ensure_preview(repo)
        await event_bus.publish(Event(type=EventType.SYSTEM_EVENT,source=request.engineer,payload={'action':'engineering_patch_created','task_id':request.task_id,'patch_id':patch.patch_id,'review_id':review.review_id}))
        return {'analysis':analysis,'implementation_plan':generated.implementation_plan,'patch':patch,'review':review}
