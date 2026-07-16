import { Navigate, Outlet } from 'react-router-dom'; import { useAuthStore } from '../stores/authStore';
export function ProtectedRoute(){ return useAuthStore(s=>s.accessToken) ? <Outlet/> : <Navigate to="/login" replace/>; }
