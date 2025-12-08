"""
Test configuration and fixtures.
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash
from app.utils.snowflake import init_snowflake


# Test database URL (PostgreSQL in Docker)
# Use environment variable or default test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:test_password@localhost/test_db"
)


# Create test engine with simple configuration
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def init_test_snowflake():
    """Initialize Snowflake ID generator for tests."""
    init_snowflake(datacenter_id=0, worker_id=0, epoch=1609459200000)  # 2021-01-01


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup after all tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    async with TestSessionLocal() as session:
        yield session



@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Get test HTTP client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user."""
    user = User(
        username="testuser",
        password=get_password_hash("Test@123456"),
        email="test@example.com",
        user_type=2,
        status=1,
        tenant_id=0
    )
    db_session.add(user)
    await db_session.commit()
    return user



@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create admin user."""
    user = User(
        username="admin",
        password=get_password_hash("admin123"),
        email="admin@example.com",
        user_type=0,  # Superadmin
        status=1,
        tenant_id=0
    )
    db_session.add(user)
    await db_session.commit()
    return user



@pytest_asyncio.fixture
async def disabled_user(db_session: AsyncSession) -> User:
    """Create disabled user."""
    user = User(
        username="disabled",
        password=get_password_hash("Test@123456"),
        email="disabled@example.com",
        user_type=2,
        status=0,  # Disabled
        tenant_id=0
    )
    db_session.add(user)
    await db_session.commit()
    return user



@pytest_asyncio.fixture
async def admin_token(client: AsyncClient, admin_user: User) -> str:
    """Get admin access token."""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["data"]["access_token"]


@pytest_asyncio.fixture
async def user_token(client: AsyncClient, test_user: User) -> str:
    """Get test user access token."""
    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "Test@123456"
    })
    return response.json()["data"]["access_token"]

