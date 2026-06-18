import os
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import sqlalchemy
from sqlalchemy import text

# Database connection pool
db = None


def init_connection_pool():
    """Initialize the database connection pool."""
    db_user = os.environ.get("DB_USER", "api-user")
    db_pass = os.environ.get("DB_PASS", "")
    db_name = os.environ.get("DB_NAME", "mydb")
    db_host = os.environ.get("DB_HOST", "127.0.0.1")
    db_port = os.environ.get("DB_PORT", "3306")

    pool = sqlalchemy.create_engine(
        f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}",
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
    )
    return pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - initialize and cleanup resources."""
    global db
    db = init_connection_pool()
    yield
    db.dispose()


app = FastAPI(
    title="GCP API",
    description="Sample API connected to Cloud SQL",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "gcp-api"}


@app.get("/api/users")
def get_users():
    """Fetch all users from Cloud SQL."""
    try:
        with db.connect() as conn:
            result = conn.execute(
                text("SELECT id, name, email, created_at FROM users"))
            users = [
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "created_at": str(row[3]),
                }
                for row in result
            ]
        return {"data": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    """Fetch a single user by ID."""
    try:
        with db.connect() as conn:
            result = conn.execute(
                text("SELECT id, name, email, created_at FROM users WHERE id = :id"),
                {"id": user_id},
            )
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
            user = {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "created_at": str(row[3]),
            }
        return {"data": user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users")
def create_user(name: str, email: str):
    """Create a new user."""
    try:
        with db.connect() as conn:
            conn.execute(
                text("INSERT INTO users (name, email) VALUES (:name, :email)"),
                {"name": name, "email": email},
            )
            conn.commit()
        return {"message": "User created", "data": {"name": name, "email": email}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    """Delete a user by ID."""
    try:
        with db.connect() as conn:
            result = conn.execute(
                text("DELETE FROM users WHERE id = :id"), {"id": user_id}
            )
            conn.commit()
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
