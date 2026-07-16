export interface User { id: string; email: string; full_name: string; is_active: boolean; created_at: string; }
export interface AuthTokens { access_token: string; refresh_token: string; token_type: 'bearer'; }
export interface AuthResponse extends AuthTokens { user: User; }
