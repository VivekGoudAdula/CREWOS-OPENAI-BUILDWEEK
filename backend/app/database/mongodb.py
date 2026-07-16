import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import get_settings
logger = logging.getLogger(__name__)
class MongoDatabase:
    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None
    async def connect(self) -> None:
        settings=get_settings(); self.client=AsyncIOMotorClient(settings.mongodb_uri,serverSelectionTimeoutMS=5000,connectTimeoutMS=5000); await self.client.admin.command('ping'); self.database=self.client[settings.mongodb_database]; logger.info('MongoDB connected')
    async def close(self) -> None:
        if self.client: self.client.close(); logger.info('MongoDB disconnected')
    def get_database(self) -> AsyncIOMotorDatabase:
        if self.database is None: raise RuntimeError('MongoDB has not been initialized')
        return self.database
mongodb = MongoDatabase()
async def get_database() -> AsyncIOMotorDatabase: return mongodb.get_database()
