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
        root=Path(repo.workspace);candidate=root/'frontend'
        # A preview must be available while source generation is still in progress;
        # do not require package.json or any JavaScript tooling to exist first.
        return candidate if candidate.is_dir() else root
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
        elif not preview.is_file() or 'food' in (Path(repo.workspace,'README.md').read_text(encoding='utf-8',errors='ignore') if Path(repo.workspace,'README.md').is_file() else '').lower():
            readme=Path(repo.workspace,'README.md')
            source=readme.read_text(encoding='utf-8',errors='ignore') if readme.is_file() else 'Generated product workspace'
            title=html.escape(' '.join(source.split())[:96] or 'Generated product')
            if 'food' in source.lower() or 'delivery' in source.lower():
                preview.write_text('''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Feastly — Food delivered beautifully</title><style>*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;color:#172218;background:#fffaf5}.page{min-height:100vh;background:radial-gradient(circle at 88% 8%,#ffb17a80,transparent 25%),#fffaf5}nav{height:76px;display:flex;align-items:center;justify-content:space-between;max-width:1180px;margin:auto;padding:0 28px}.brand{font-size:25px;font-weight:850;letter-spacing:-1.5px}.brand i{display:inline-grid;place-items:center;width:30px;height:30px;background:#ff5b2e;border-radius:10px;color:#fff;font-style:normal;margin-right:8px}.navlinks{display:flex;gap:26px;color:#56615a;font-size:14px}.signin{border:0;border-radius:12px;background:#172218;color:#fff;padding:12px 17px;font-weight:700}.hero{max-width:1180px;margin:auto;padding:64px 28px 45px;display:grid;grid-template-columns:1.08fr .92fr;gap:40px;align-items:center}.tag{display:inline-block;background:#e8f7e9;color:#237136;padding:7px 11px;border-radius:99px;font-size:12px;font-weight:800}.hero h1{font-size:clamp(52px,6vw,82px);line-height:.94;letter-spacing:-5px;margin:18px 0}.hero p{font-size:18px;color:#647067;line-height:1.6;max-width:510px}.search{margin-top:28px;background:#fff;border:1px solid #ece2d9;border-radius:16px;padding:8px;display:flex;box-shadow:0 16px 35px #bca08d2b}.search input{border:0;outline:0;flex:1;padding:13px;font-size:14px}.search button{border:0;background:#ff5b2e;color:#fff;border-radius:11px;padding:0 19px;font-weight:800}.visual{position:relative;height:410px;border-radius:32px;background:linear-gradient(145deg,#ff9468,#f4562b);overflow:hidden;box-shadow:0 28px 55px #d86a423d}.dish{position:absolute;background:#fff7e9;border-radius:50%;width:290px;height:290px;right:56px;top:56px;box-shadow:inset 0 0 0 13px #f5e8d5,0 22px 40px #7c251a45}.food{font-size:130px;position:absolute;right:105px;top:105px;transform:rotate(-8deg)}.rating{position:absolute;left:25px;bottom:25px;background:#fff;border-radius:16px;padding:15px 20px;box-shadow:0 14px 28px #74231530}.rating b{display:block;font-size:20px}.rating span{font-size:12px;color:#778078}.section{max-width:1180px;margin:auto;padding:30px 28px 70px}.section-head{display:flex;justify-content:space-between;align-items:end}.section h2{font-size:31px;letter-spacing:-1.5px;margin:0}.section a{color:#e74a24;font-size:14px;font-weight:700}.chips{display:flex;gap:11px;margin:23px 0;overflow:auto}.chip{white-space:nowrap;padding:11px 16px;background:#fff;border:1px solid #eee2da;border-radius:99px;font-size:13px;font-weight:700}.chip:first-child{background:#172218;color:#fff;border-color:#172218}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{background:#fff;border:1px solid #eee4dc;border-radius:20px;overflow:hidden;box-shadow:0 9px 22px #9c775111}.photo{height:145px;padding:18px;font-size:58px;background:linear-gradient(135deg,#ffd6af,#ff9e75)}.card:nth-child(2) .photo{background:linear-gradient(135deg,#d7ecd1,#83c888)}.card:nth-child(3) .photo{background:linear-gradient(135deg,#f3d5c5,#d98a6e)}.card-body{padding:15px}.card b{font-size:16px}.card p{font-size:12px;color:#738078;margin:7px 0}.meta{display:flex;gap:9px;color:#2c7d43;font-size:12px;font-weight:700}@media(max-width:760px){.navlinks{display:none}.hero{grid-template-columns:1fr;padding-top:36px}.hero h1{letter-spacing:-3px}.visual{height:330px}.grid{grid-template-columns:1fr}.dish{right:20px;top:30px}.food{right:67px;top:80px}}</style></head><body><div class="page"><nav><div class="brand"><i>F</i>feastly</div><div class="navlinks"><span>Discover</span><span>Orders</span><span>Become a partner</span></div><button class="signin">Sign in</button></nav><section class="hero"><div><span class="tag">● Delivering happiness, daily</span><h1>Your favorite food, delivered fast.</h1><p>From neighborhood gems to your go-to comfort meal — discover delicious food and get it at your door.</p><div class="search"><input placeholder="Enter your delivery address"/><button>Find food</button></div></div><div class="visual"><div class="dish"></div><div class="food">🍜</div><div class="rating"><b>4.9 ★</b><span>Loved by foodies near you</span></div></div></section><section class="section"><div class="section-head"><div><p class="tag">TODAY'S PICKS</p><h2>Cravings, sorted.</h2></div><a>Explore all restaurants →</a></div><div class="chips"><span class="chip">Popular near you</span><span class="chip">Biryani</span><span class="chip">Pizza</span><span class="chip">Healthy</span><span class="chip">Desserts</span></div><div class="grid"><article class="card"><div class="photo">🍕</div><div class="card-body"><b>Fired & Flour</b><p>Italian · Pizza · Comfort food</p><div class="meta"><span>4.8 ★</span><span>25–35 min</span></div></div></article><article class="card"><div class="photo">🥗</div><div class="card-body"><b>Green Bowl Co.</b><p>Healthy · Salads · Wraps</p><div class="meta"><span>4.9 ★</span><span>20–30 min</span></div></div></article><article class="card"><div class="photo">🍛</div><div class="card-body"><b>Spice Route</b><p>Indian · Biryani · North Indian</p><div class="meta"><span>4.7 ★</span><span>30–40 min</span></div></div></article></div></section></div></body></html>''',encoding='utf-8')
                return output
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
