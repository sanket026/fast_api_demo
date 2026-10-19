# FastAPI MySQL Docker Demo

A production-ready, clean-architecture demonstration project showcasing how to build, run, test, and deploy a Python [FastAPI](https://fastapi.tiangolo.com/) application backed by MySQL 8.0, managed with Alembic database migrations, and orchestrated with Docker Compose.

---

## Architecture & Directory Structure

This project follows clean code and layered architecture principles:
- **Presentation Layer (`app/api/`)**: FastAPI routers, path/query validation, HTTP response status codes.
- **Business Logic Layer (`app/services/`)**: Domain validations, duplicate constraint handling, transaction orchestration.
- **Data Access Layer (`app/repositories/`)**: SQLAlchemy 2.0 database queries and data mutations.
- **Domain Models & Persistence (`app/db/`)**: Declarative models, session lifecycle, connection pooling.
- **Validation Schemas (`app/schemas/`)**: Pydantic v2 schemas for request validation and response serialization.
- **Core Configuration (`app/core/`)**: Type-safe settings via `pydantic-settings`, centralized logging, and domain exception handlers.
- **Database Migrations (`alembic/`)**: Versioned schema changes decoupled from application startup.
- **Automated Tests (`tests/`)**: Isolated test suite with in-memory SQLite and mock fixtures.

```text
fastapi-demo/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application factory & lifespan
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py           # /health and /health/ready endpoints
│   │       └── users.py            # User CRUD endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Pydantic BaseSettings & DB URL logic
│   │   ├── logging.py              # Centralized logging configuration
│   │   └── exceptions.py           # Domain exceptions & global exception handlers
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                 # DeclarativeBase definition
│   │   ├── session.py              # Engine pooling & get_db dependency
│   │   └── models/
│   │       ├── __init__.py
│   │       └── user.py             # User SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py                 # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py         # User business logic & transaction handling
│   └── repositories/
│       ├── __init__.py
│       └── user_repository.py      # SQLAlchemy query repository
├── alembic/
│   ├── env.py                      # Alembic environment linked to settings & models
│   ├── script.py.mako              # Revision file template
│   └── versions/
│       └── 2026_10_19_0001_initial_users.py # Initial users table migration
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Test fixtures & isolated SQLite test DB
│   ├── test_health.py              # Health check & readiness tests
│   └── test_users.py               # Comprehensive CRUD, validation & pagination tests
├── .dockerignore                   # Build context exclusion
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignored files
├── alembic.ini                     # Alembic configuration
├── Dockerfile                      # Production-ready multi-stage / non-root image
├── compose.yaml                    # Docker Compose orchestrating API and MySQL
├── compose.override.yaml.example   # Optional dev volume mount and --reload override
├── requirements.txt                # Pinned Python package dependencies
├── pytest.ini                      # Pytest runner configuration
├── Makefile                        # Convenient development commands
├── app.api                         # API contract documentation
├── firebase.json                   # Route specifications and rewrites
└── README.md                       # Complete documentation
```

---

## Prerequisites

- **Docker**: Version 20.10+ (Docker Engine with Compose v2)
- **Python**: Version 3.10+ (if running or testing outside Docker)
- **Make**: (Optional, for Makefile convenience shortcuts)

---

## Quickstart with Docker Compose

### 1. Configure the Environment

Copy the example environment file to `.env`:

```bash
cp .env.example .env
```

Review the values in `.env`. By default, it is preconfigured to work out of the box with the MySQL Docker container:

```dotenv
APP_NAME=FastAPI Demo
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
APP_PORT=8000

MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_HOST_PORT=3307
MYSQL_DATABASE=fastapi_demo
MYSQL_USER=fastapi_user
MYSQL_PASSWORD=change_me
MYSQL_ROOT_PASSWORD=change_root_me

DATABASE_URL=
```

> **Note on Port Configuration**:
> - `APP_PORT` defines the host port mapped to container port `8000`. If port `8000` is already in use by a host service (such as gunicorn), change `APP_PORT` to `8002` in `.env`.
> - `MYSQL_HOST_PORT` defines the host port mapped to MySQL container port `3306` (defaults to `3307` to prevent conflict with local host databases).
> - Inside Docker Compose, the API always connects internally via `db:3306`.
>
> **Note on `DATABASE_URL`**: If `DATABASE_URL` is empty, the application automatically computes it from the `MYSQL_*` parameters:
> `mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4`

### 2. Build and Start the Containers

Start both the FastAPI API service and MySQL 8.0:

```bash
docker compose up --build -d
```

### 3. Check Container Health Status

```bash
docker compose ps
```

Expected output:
Both `fastapi_demo_api` and `fastapi_demo_db` will transition to `healthy`. The API service automatically waits for MySQL's health check before starting.

### 4. Run Database Migrations

Apply database migrations using Alembic inside the running API container:

```bash
docker compose exec api alembic upgrade head
```

### 5. Follow API Logs

```bash
docker compose logs -f api
```

### 6. Run the Test Suite Inside Docker

```bash
docker compose exec api pytest
```

### 7. Stopping Containers

- **Stop containers preserving database data**:
  ```bash
  docker compose down
  ```
- **Stop containers and permanently delete MySQL data volume**:
  ```bash
  docker compose down -v
  ```
  > ⚠️ **Warning**: `docker compose down -v` removes the named Docker volume (`fastapi_demo_mysql_data`) and permanently deletes all stored MySQL records.

---

## API Documentation & Interactive Docs

Once running, the interactive documentation is available in your browser:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## API Endpoints & cURL Examples

### 1. Health Endpoints

#### Operational Health
```bash
curl -i http://localhost:8000/health
```
Response (`200 OK`):
```json
{
  "status": "ok",
  "app": "FastAPI Demo",
  "environment": "development"
}
```

#### Database Readiness Ping
```bash
curl -i http://localhost:8000/health/ready
```
Response (`200 OK`):
```json
{
  "status": "ready",
  "database": "connected"
}
```

---

### 2. User CRUD Endpoints

#### Create a User
```bash
curl -i -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.doe@example.com",
    "username": "janedoe",
    "full_name": "Jane Doe",
    "is_active": true
  }'
```
Response (`201 Created`):
```json
{
  "email": "jane.doe@example.com",
  "username": "janedoe",
  "full_name": "Jane Doe",
  "is_active": true,
  "id": 1,
  "created_at": "2026-10-19T05:00:00Z",
  "updated_at": "2026-10-19T05:00:00Z"
}
```

#### List Users with Pagination
```bash
curl -i "http://localhost:8000/api/v1/users?skip=0&limit=10"
```
Response (`200 OK`):
```json
{
  "items": [
    {
      "email": "jane.doe@example.com",
      "username": "janedoe",
      "full_name": "Jane Doe",
      "is_active": true,
      "id": 1,
      "created_at": "2026-10-19T05:00:00Z",
      "updated_at": "2026-10-19T05:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### Get User by ID
```bash
curl -i http://localhost:8000/api/v1/users/1
```

#### Update User
```bash
curl -i -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane M. Doe",
    "is_active": true
  }'
```

#### Delete User
```bash
curl -i -X DELETE http://localhost:8000/api/v1/users/1
```
Response (`204 No Content`).

---

## Local Development Without Docker

If you prefer to run the application directly on your host machine:

### 1. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows (cmd):
# .venv\Scripts\activate.bat
# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Local Environment Variables

Update `.env` to point to your local MySQL instance:
```dotenv
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=fastapi_demo
MYSQL_USER=fastapi_user
MYSQL_PASSWORD=change_me
```

Or for instant zero-dependency testing, point to a local SQLite database:
```dotenv
DATABASE_URL=sqlite:///./local_dev.db
```

### 4. Run Migrations Locally

```bash
alembic upgrade head
```

### 5. Start the Local Server with Auto-Reload

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Development vs. Production Configuration

| Concern | Production Mode (`compose.yaml` / `Dockerfile`) | Development Mode (`compose.override.yaml`) |
| :--- | :--- | :--- |
| **Hot Reload** | Disabled (`uvicorn app.main:app`) | Enabled (`--reload`) |
| **Code Mounting**| Source code baked into Docker image layer | Host directory mounted to `/app` for live edits |
| **Debug Mode** | `DEBUG=false` | `DEBUG=true` (verbose logs, error details) |
| **Security** | Runs under unprivileged user `appuser` (UID 1000) | Runs under `appuser` |
| **Secrets** | Injected via secure secrets manager / env files | Injected via `.env` |

To enable hot reloading with Docker Compose:
```bash
cp compose.override.yaml.example compose.override.yaml
docker compose up -d
```
Docker Compose automatically loads `compose.override.yaml` whenever present.

---

## Database Migrations with Alembic

Creating a new schema migration:

```bash
# Run inside Docker:
docker compose exec api alembic revision --autogenerate -m "add_new_column"

# Or run locally:
alembic revision --autogenerate -m "add_new_column"
```

Applying migrations:
```bash
docker compose exec api alembic upgrade head
```

Reverting the last migration:
```bash
docker compose exec api alembic downgrade -1
```

---

## Running the Automated Test Suite

The test suite runs using **Pytest** with an isolated in-memory SQLite database:
- **No MySQL database is touched** during testing.
- Tests execute fast and independently.
- Database connection failure states are verified using mock fixtures.

To execute tests:

```bash
# Inside Docker container:
docker compose exec api pytest

# Locally in virtual environment:
pytest
```

---

## Troubleshooting

### 1. `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")`
- **Cause**: The API container is attempting to connect before MySQL is ready, or using `localhost` instead of `db`.
- **Solution**: Ensure `MYSQL_HOST=db` when running inside Docker. Docker Compose is already configured with `depends_on: db: condition: service_healthy` so the API will wait until MySQL passes its ping check.

### 2. `Authentication plugin 'caching_sha2_password' cannot be loaded`
- **Cause**: MySQL 8.0 default authentication plugin requires `cryptography`.
- **Solution**: The `cryptography` package is pinned in `requirements.txt` and installed in the Docker image.

### 3. Port 3306 or 8000 is Already in Use
- **Cause**: Another local MySQL service or web server is running on your host machine.
- **Solution**: Modify the host port binding in `compose.yaml`, e.g., `"8001:8000"` or `"3307:3306"`.

### 4. Database Volume Permissions
- **Cause**: Docker volume created with conflicting UID.
- **Solution**: Run `docker compose down -v` and rebuild with `docker compose up --build -d`.
