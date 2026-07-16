import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.database.mongodb import mongodb
from app.runtime.bootstrap import bootstrap_runtime
from app.runtime.container import runtime
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')
@asynccontextmanager
async def lifespan(_:FastAPI):
    try:
        await mongodb.connect(); runtime.projects.set_database(mongodb.get_database()); runtime.memory.set_database(mongodb.get_database()); runtime.collaboration.set_database(mongodb.get_database()); runtime.decisions.set_database(mongodb.get_database())
    except Exception:
        logging.exception('MongoDB unavailable; API started without persistence. Authentication requires MongoDB.')
    if not runtime.agents: runtime.agents=await bootstrap_runtime(runtime)
    yield
    for agent in runtime.agents: await agent.shutdown()
    runtime.agents=[]
    await mongodb.close()
settings=get_settings()
app=FastAPI(title=settings.app_name,debug=settings.debug,lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.get('/health',tags=['Health'])
async def health(): return {'status':'healthy'}
app.include_router(api_router,prefix=settings.api_v1_prefix)
register_exception_handlers(app)
