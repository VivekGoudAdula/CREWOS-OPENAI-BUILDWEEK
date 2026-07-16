import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../services/api';

type Repository = { repository_id: string; workspace: string; project_id?: string };

export function EngineeringPage() {
  const [params] = useSearchParams();
  const projectId = params.get('project');
  const [name, setName] = useState('');
  const [repos, setRepos] = useState<Repository[]>([]);
  const [selected, setSelected] = useState<Repository>();
  const [tree, setTree] = useState<string[]>([]);
  const [patches, setPatches] = useState<any[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string>();
  const [preview, setPreview] = useState(Boolean(projectId));
  const [file, setFile] = useState<{ path: string; content: string }>();
  const [error, setError] = useState('');

  const choose = async (repo: Repository) => {
    setSelected(repo);
    setFile(undefined);
    setPreviewUrl(undefined);
    try {
      const [treeResult, previewResult] = await Promise.all([
        api.get(`/repository/${repo.repository_id}/tree`),
        api.get(`/repository/${repo.repository_id}/preview`),
      ]);
      setTree(treeResult.data);
      const backendOrigin = String(api.defaults.baseURL).replace(/\/api\/v1\/?$/, '');
      setPreviewUrl(`${backendOrigin}${previewResult.data.url}`);
      setError('');
    } catch {
      setTree([]);
      setPreviewUrl(undefined);
      setError('The workspace is still preparing its preview. Please wait a moment.');
    }
  };

  const load = async () => {
    try {
      const calls = [api.get('/repository', { params: projectId ? { project_id: projectId } : undefined }), api.get('/engineering/patches')];
      if (projectId) calls.push(api.get(`/projects/${projectId}`));
      const [repositories, patchResult, project] = await Promise.all(calls) as any[];
      setRepos(repositories.data);
      setPatches(patchResult.data);
      if (project?.data?.name) setName(project.data.name);
      if (repositories.data.length === 1 && repositories.data[0].repository_id !== selected?.repository_id) await choose(repositories.data[0]);
    } catch {
      setError('Unable to reach the engineering workspace right now.');
    }
  };

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 4000);
    return () => window.clearInterval(timer);
  }, [projectId]);

  const openFile = async (path: string) => {
    if (!selected) return;
    try { setFile((await api.get(`/repository/${selected.repository_id}/file`, { params: { path } })).data); }
    catch { setError('Select the workspace again to open files.'); }
  };

  const retry = async () => {
    if (!projectId) return;
    try { await api.post(`/engineering/projects/${projectId}/retry`); await load(); }
    catch (requestError: any) { setError(requestError?.response?.data?.detail || 'Could not restart source generation.'); }
  };

  const workspaceName = name || 'Generated workspace';
  const relevant = selected?.project_id ? patches.filter((patch) => patch.task_id.includes(selected.project_id)) : patches;
  const title = file?.path || (selected?.project_id ? workspaceName : 'Repository Explorer');

  return <main className="engineering">
    <header><p className="eyebrow">Engineering Department</p><h1>{name ? `${name} workspace` : 'Generated workspace'}</h1><p>Inspect the generated repository, live product preview, source files, and patches.</p></header>
    {projectId && <div className="preview-toolbar"><div><span className="preview-dot" /> Live generated UI</div><button type="button" onClick={() => setPreview((value) => !value)}>{preview ? 'Hide preview' : 'Show preview'}</button>{previewUrl && <a href={previewUrl} target="_blank" rel="noreferrer">Open in new tab ↗</a>}</div>}
    {projectId && preview && <section className="live-preview"><div className="preview-frame-title"><span>{workspaceName}</span><small>{previewUrl ? 'Ready' : 'Preparing preview…'}</small></div>{previewUrl ? <iframe title={`${workspaceName} live preview`} src={previewUrl} sandbox="allow-scripts allow-same-origin allow-forms" /> : <div className="preview-loading"><span className="preview-dot" /> Building a secure live preview for this generated app…</div>}</section>}
    {projectId && !relevant.length && <button className="retry-generation" type="button" onClick={retry}>Retry source generation</button>}
    {error && <p className="engineering-error">{error}</p>}
    <div className="eng-grid"><section className="repo-list"><h2>Repositories</h2>{repos.map((repo) => <button key={repo.repository_id} onClick={() => choose(repo)} className={selected?.repository_id === repo.repository_id ? 'selected' : ''}><b>{repo.project_id ? workspaceName : repo.workspace}</b><small>Generated workspace</small></button>)}{!repos.length && <p className="empty">Engineering is creating the workspace.</p>}</section><section className="file-panel"><div className="panel-title"><h2>{title}</h2>{selected && <span>{tree.length} files</span>}</div>{file ? <pre className="source-view">{file.content}</pre> : selected ? <div className="source-browser">{tree.map((path) => <button key={path} onClick={() => openFile(path)}>File · {path}</button>)}</div> : <div className="empty">Generated files will appear here.</div>}</section></div>
    <section className="patch-panel"><div className="panel-title"><h2>AI patches & review</h2><span>{relevant.length} patches</span></div>{relevant.map((patch) => <article key={patch.patch_id}><b>Patch {patch.patch_id.slice(0, 8)}</b><p>{patch.summary}</p><pre>{patch.unified_diff || 'No diff available yet.'}</pre></article>)}{!relevant.length && <p className="empty">Patches appear once generation completes.</p>}</section>
  </main>;
}
