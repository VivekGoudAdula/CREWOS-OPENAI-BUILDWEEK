import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
type DebugPageProps={title:string;path:string}
export function RuntimeDebugPage({title,path}:DebugPageProps){const {data,isLoading,error}=useQuery({queryKey:[path],queryFn:()=>api.get(path).then(r=>r.data),refetchInterval:5000});return <><h1 className="text-2xl font-semibold">{title}</h1><p className="mt-2 text-sm text-zinc-500">Refreshes every five seconds.</p>{isLoading?<p className="mt-6">Loading…</p>:error?<p className="mt-6 text-red-600">Runtime API is unavailable.</p>:<pre className="mt-6 overflow-auto rounded border bg-zinc-50 p-4 text-xs">{JSON.stringify(data,null,2)}</pre>}</>}
