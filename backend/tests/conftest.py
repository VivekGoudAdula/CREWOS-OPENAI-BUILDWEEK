import os
os.environ.setdefault('JWT_SECRET_KEY', 'test-only-secret')
import pytest
from app.database.mongodb import mongodb
@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    async def connect(): return None
    async def close(): return None
    monkeypatch.setattr(mongodb, 'connect', connect)
    monkeypatch.setattr(mongodb, 'close', close)
