from datetime import timedelta
from fastapi.testclient import TestClient
from app.api.v1.auth import service
from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, decode_token
from app.main import app
from app.schemas.common import utcnow
from app.schemas.user import AuthResponse, AuthTokens, User

USER=User(id='507f1f77bcf86cd799439011',email='ada@example.com',full_name='Ada',is_active=True,created_at=utcnow(),updated_at=utcnow())
class FakeAuthService:
    async def register(self, payload): return AuthResponse(user=USER,access_token='access',refresh_token='refresh')
    async def login(self, email, password): return AuthResponse(user=USER,access_token='access',refresh_token='refresh')
    def tokens(self, user_id): return AuthTokens(access_token='next-access',refresh_token='next-refresh')
def test_register_login_and_protected_route():
    app.dependency_overrides[service]=lambda:FakeAuthService()
    app.dependency_overrides[get_current_user]=lambda:USER
    with TestClient(app) as client:
        assert client.post('/api/v1/auth/register',json={'email':'ada@example.com','full_name':'Ada','password':'password123'}).status_code==201
        assert client.post('/api/v1/auth/login',json={'email':'ada@example.com','password':'password123'}).json()['user']['email']=='ada@example.com'
        assert client.get('/api/v1/auth/me').json()['id']==USER.id
    app.dependency_overrides.clear()
def test_jwt_validation():
    token=create_access_token(USER.id)
    assert decode_token(token,'access')['sub']==USER.id
