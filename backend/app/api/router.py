from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.runtime import router as runtime_router
from app.api.v1.projects import router as projects_router
from app.api.v1.collaboration import router as collaboration_router
from app.api.v1.engineering import router as engineering_router
from app.api.v1.qa import router as qa_router
from app.api.v1.insights import router as insights_router
api_router=APIRouter(); api_router.include_router(auth_router); api_router.include_router(runtime_router); api_router.include_router(projects_router); api_router.include_router(collaboration_router); api_router.include_router(engineering_router); api_router.include_router(qa_router); api_router.include_router(insights_router)
