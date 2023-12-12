from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends

MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "cloud_management"

async def get_database() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(MONGO_DETAILS)
    return client[DB_NAME]

#dependcy for the routes
async def get_db(database: AsyncIOMotorClient = Depends(get_database)):
    return database