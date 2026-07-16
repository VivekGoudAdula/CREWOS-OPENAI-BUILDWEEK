"""Run after both services are started: python scripts/smoke_test.py."""
import os
from uuid import uuid4
import requests

api=os.getenv('API_URL','http://localhost:8000')
frontend=os.getenv('FRONTEND_URL','http://localhost:5173')
health=requests.get(f'{api}/health',timeout=5); health.raise_for_status(); assert health.json()['status']=='healthy'
email=f'smoke-{uuid4().hex[:10]}@example.test'
registration=requests.post(f'{api}/api/v1/auth/register',json={'email':email,'full_name':'Smoke Test','password':'SmokePass123!'},timeout=5); registration.raise_for_status()
login=requests.post(f'{api}/api/v1/auth/login',json={'email':email,'password':'SmokePass123!'},timeout=5); login.raise_for_status()
token=login.json()['access_token']
current=requests.get(f'{api}/api/v1/auth/me',headers={'Authorization':f'Bearer {token}'},timeout=5); current.raise_for_status(); assert current.json()['email']==email
ui=requests.get(frontend,timeout=5); ui.raise_for_status()
print('Smoke check passed: MongoDB/authentication and frontend are reachable.')
