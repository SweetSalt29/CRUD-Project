import asyncio
from app.database import engine
from app.models import Base

async def clear_database():
    print("Connecting to database to clear tables...")
    async with engine.begin() as conn:
        # This will delete all tables and recreate them empty
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Done! Database is now empty and IDs are reset.")

if __name__ == "__main__":
    asyncio.run(clear_database())