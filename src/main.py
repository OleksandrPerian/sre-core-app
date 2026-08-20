import os
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI, HTTPException, status

DB_USER = os.environ.get("DB_USER", "visitor_app_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME", "visitor_db")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(
        host=DB_HOST,
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

@app.get("/healthz", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Liveness probe: verifies Python process is responsive. NO DB CALLS!"""
    return {"status": "ok"}

@app.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness probe: verifies PostgreSQL connection pool is active."""
    try:
        async with app.state.db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable"
        )

@app.post("/visit")
async def record_visit(visitor_id: str):
    async with app.state.db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO visits (visitor_id) VALUES ($1)",
            visitor_id
        )
        return {"status": "success", "recorded": visitor_id}

@app.get("/stats")
async def get_stats(): 
    async with app.state.db_pool.acquire() as conn:
        total_visits = await conn.fetchval("SELECT COUNT(*) FROM visits")
    return {"total_visits": total_visits}