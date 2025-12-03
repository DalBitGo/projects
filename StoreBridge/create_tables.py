"""Create database tables directly."""
import asyncio
from app.database import get_engine
from app.models.base import Base
from app.models.product import Product, ProductRegistration, Job, CategoryMapping  # noqa: F401


async def create_tables():
    """Create all tables."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables created successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables())
