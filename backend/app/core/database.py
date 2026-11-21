import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db_manager = DatabaseManager()

async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    try:
        db_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000
        )
        db_manager.db = db_manager.client[settings.DATABASE_NAME]
        # Ping the database
        await db_manager.client.admin.command('ping')
        logger.info("MongoDB connected successfully!")
        await create_indexes()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Note: Do not crash application so unit tests or mock modes can run if needed

async def close_mongo_connection():
    if db_manager.client:
        logger.info("Closing MongoDB connection...")
        db_manager.client.close()
        logger.info("MongoDB connection closed.")

async def create_indexes():
    """Ensure indexes exist on primary collections for performance and isolation."""
    if db_manager.db is None:
        return
    try:
        # Users
        await db_manager.db.users.create_index("email", unique=True)
        # Profiles
        await db_manager.db.profiles.create_index("userId", unique=True)
        # Campaigns
        await db_manager.db.campaigns.create_index([("userId", 1), ("createdAt", -1)])
        # Companies
        await db_manager.db.companies.create_index("name")
        await db_manager.db.companies.create_index("website")
        # Contacts
        await db_manager.db.contacts.create_index([("companyId", 1), ("name", 1)])
        await db_manager.db.contacts.create_index("professionalEmail")
        # Drafts
        await db_manager.db.emailDrafts.create_index([("campaignId", 1), ("userId", 1)])
        await db_manager.db.emailDrafts.create_index("contactId")
        # Executions
        await db_manager.db.agentExecutions.create_index([("campaignId", 1), ("startedAt", -1)])
        logger.info("Database indexes ensured.")
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")

def get_database() -> AsyncIOMotorDatabase:
    return db_manager.db
