# GCP API

A Python FastAPI application that connects to Cloud SQL (PostgreSQL) and deploys to Cloud Run.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/api/users` | Fetch all users |
| GET | `/api/users/{id}` | Fetch user by ID |
| POST | `/api/users?name=x&email=y` | Create a user |
| DELETE | `/api/users/{id}` | Delete a user |

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_USER=api-user
export DB_PASS=yourpassword
export DB_NAME=mydb
export DB_HOST=127.0.0.1

# Run the app
uvicorn app.main:app --reload --port 8080
```

## Docker

```bash
docker build -t gcp-api .
docker run -p 8080:8080 -e DB_USER=api-user -e DB_PASS=pass -e DB_NAME=mydb -e DB_HOST=host gcp-api
```

## Deployment

Push to `main` branch triggers GitHub Actions which:
1. Authenticates to GCP via Workload Identity Federation
2. Builds Docker image
3. Pushes to Artifact Registry
4. Deploys to Cloud Run

## Cloud SQL Table Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
