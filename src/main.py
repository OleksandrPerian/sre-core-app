import os
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI

DB_USER = os.environ.get("DB_USER", "visitor_app_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME", "visitor_db")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
   )
    async with app.state.db_pool.acquire() as conn:
        await conn.execute(""" 
        CREATE TABLE IF NOT EXISTS visits (
            id SERIAL PRIMARY KEY,
            visitor_id VARCHAR(100) NOT NULL,
            visited_at TIMESTAMP DEFAULT NOW()
        );
      """)

    yield

    await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)