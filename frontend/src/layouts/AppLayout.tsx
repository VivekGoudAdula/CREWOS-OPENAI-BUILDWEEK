import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { AppBackground } from '../components/AppBackground';
import { useAuthStore } from '../stores/authStore';

const productLinks = [
  ['CH', 'Chat', '/planning'], ['MC', 'Mission Control', '/dashboard'], ['PR', 'Projects', '/projects'],
  ['DP', 'Departments', '/agents'], ['EN', 'Engineering', '/engineering'], ['QA', 'Quality', '/quality'],
  ['AN', 'Analytics', '/analytics'], ['HI', 'History', '/history'], ['ST', 'Settings', '/settings'],
] as const;
const developerLinks = [['RT', 'Runtime', '/runtime'], ['RG', 'Registry', '/registry'], ['MM', 'Memory', '/memory'], ['EV', 'Events', '/events']] as const;

function Navigation({ items }: { items: readonly (readonly [string, string, string])[] }) {
  return <nav className="product-nav">{items.map(([mark, label, to]) => <NavLink key={to} to={to} className={({ isActive }) => `product-nav-link ${isActive ? 'active' : ''}`}><span className="nav-mark">{mark}</span><span>{label}</span></NavLink>)}</nav>;
}

export function AppLayout() {
  const navigate = useNavigate();
  const logout = useAuthStore(state => state.logout);
  const signOut = () => { logout(); navigate('/login', { replace: true }); };
  return <div className="app-shell enterprise-shell min-h-screen md:grid md:grid-cols-[264px_1fr]">
    <AppBackground soft />
    <aside className="enterprise-sidebar">
      <NavLink to="/dashboard" className="brand enterprise-brand"><img src="/logo.png" alt="CrewOS" /></NavLink>
      <p className="nav-section-label">Workspace</p><Navigation items={productLinks} />
      <div className="nav-divider" />
      <p className="nav-section-label">Developer tools</p><Navigation items={developerLinks} />
      <button className="sidebar-logout" type="button" onClick={signOut}>Log out</button>
    </aside>
    <main className="enterprise-main">
      <header className="enterprise-topbar"><div><span className="topbar-kicker">CREWOS</span><span className="topbar-title">Autonomous software company</span></div><div className="topbar-actions"><span className="topbar-status"><i /> All systems live</span><button className="account-button" type="button">Account <span>›</span></button></div></header>
      <section className="enterprise-content"><Outlet /></section>
    </main>
  </div>;
}
