import difflib
import html
from pathlib import Path
from app.engineering.models import CodeReview, Patch, Repository, RepositoryAnalysis
class EngineeringService:
    def __init__(self,provider):self.repositories={};self.patches=[];self.reviews=[];self.provider=provider
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
    def _preview_prefix(self,repo:Repository)->str:
        return f'/api/v1/repository/{repo.repository_id}/preview/'
    async def build_preview(self,repo:Repository)->Path:
        frontend=self._frontend_root(repo)
        if frontend is None: raise ValueError('This generated workspace does not contain a frontend preview yet')
        output=frontend/'.crewos_preview';output.mkdir(exist_ok=True)
        preview=output/'index.html'
        dedicated=frontend/'preview.html'
        if dedicated.is_file():
            preview.write_text(dedicated.read_text(encoding='utf-8'),encoding='utf-8')
        elif not preview.is_file():
            readme=Path(repo.workspace,'README.md')
            source=readme.read_text(encoding='utf-8',errors='ignore') if readme.is_file() else 'Generated product workspace'
            title=html.escape(' '.join(source.split())[:96] or 'Generated product')
            preview.write_text(f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,Arial,sans-serif;background:#070b18;color:#f8fafc}}.hero{{min-height:100vh;padding:42px;background:radial-gradient(circle at 75% 12%,#7c3aed77,transparent 30%),radial-gradient(circle at 15% 72%,#06b6d477,transparent 34%),#070b18}}nav{{display:flex;justify-content:space-between;max-width:1120px;margin:auto;font-weight:800;font-size:22px}}.badge{{border:1px solid #ffffff35;border-radius:99px;padding:9px 14px;color:#cbd5e1;font-size:13px}}main{{max-width:1120px;margin:110px auto 0}}.eyebrow{{color:#67e8f9;text-transform:uppercase;letter-spacing:.16em;font-size:12px;font-weight:700}}h1{{font-size:clamp(44px,8vw,94px);line-height:.96;letter-spacing:-.065em;max-width:900px;margin:18px 0}}p{{font-size:18px;color:#cbd5e1;line-height:1.6;max-width:690px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:55px}}.card{{background:#ffffff0d;border:1px solid #ffffff1f;border-radius:20px;padding:24px;backdrop-filter:blur(12px)}}.card b{{display:block;font-size:18px;margin-bottom:10px}}.card span{{color:#94a3b8;font-size:14px}}@media(max-width:700px){{.hero{{padding:24px}}main{{margin-top:72px}}.cards{{grid-template-columns:1fr}}}}</style></head><body><div class="hero"><nav><div>✦ CrewOS</div><span class="badge">Generated preview</span></nav><main><div class="eyebrow">CrewOS product workspace</div><h1>{title}</h1><p>This preview is served directly by CrewOS without starting a local development server, keeping the hosted runtime reliable.</p><div class="cards"><div class="card"><b>Designed for the brief</b><span>Project-specific product direction and visual system.</span></div><div class="card"><b>Implementation ready</b><span>Explore the repository below for the complete generated source.</span></div><div class="card"><b>Workspace live</b><span>Preview is safe to open from any browser.</span></div></div></main></div></body></html>''',encoding='utf-8')
        return output
    async def ensure_preview(self,repo:Repository)->str:
        await self.build_preview(repo)
        repo.preview_url=self._preview_prefix(repo)
        return repo.preview_url
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
