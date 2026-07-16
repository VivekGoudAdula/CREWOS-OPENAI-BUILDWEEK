import Strands from './Strands.jsx';
import './brandSizing.css';
import './enterprise.css';
export function AppBackground({soft=false}:{soft?:boolean}){return <div className={`app-background ${soft?'app-background-soft':''}`} aria-hidden="true"><Strands colors={['#F97316','#7C3AED','#06B6D4']} count={4} speed={0.32} amplitude={1.35} waviness={0.65} thickness={0.85} glow={2.5} taper={1.7} spread={1.15} intensity={0.55} saturation={1.3} opacity={0.9} scale={2.4}/></div>}
