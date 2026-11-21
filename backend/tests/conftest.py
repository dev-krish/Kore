import pytest
from app.core.database import connect_to_mongo, close_mongo_connection
from app.engine.registry import init_default_tools

@pytest.fixture(autouse=True)
async def setup_test_environment():
    await connect_to_mongo()
    init_default_tools()
    yield
    await close_mongo_connection()
