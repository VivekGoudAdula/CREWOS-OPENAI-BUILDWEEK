from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase): self.collection=db['users']
    async def find_by_email(self,email:str): return await self.collection.find_one({'email':email.lower()})
    async def find_by_id(self,user_id:str):
        if not ObjectId.is_valid(user_id): return None
        return await self.collection.find_one({'_id':ObjectId(user_id)})
    async def create(self, document:dict):
        result=await self.collection.insert_one(document); return await self.collection.find_one({'_id':result.inserted_id})
