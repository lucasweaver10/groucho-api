# Infrastructure

Two main containers:
- Backend API:
  - Service: fastapi
  - Container: groucho-api
  - FastAPI application
- Database Details:
  - Container: postgres-main
  - Port Mapping: 5432:5432
  - Credentials:
    - Database: agentgroucho
    - Username: postgres
    - Password: postgres
  - Connection String:
    - `DATABASE_URL = "postgresql://postgres:postgres@postgres-main:5432/agentgroucho"`
  - SQLModel and SQLAlchemy are used for ORM and database interactions
  - Connection pooling is configured with `pool_pre_ping` and `pool_recycle` settings

# Testing

The test suite uses pytest with a dedicated test database:
- Test Database:
  - Name: agentgroucho
  - Connection: `postgresql://postgres:postgres@postgres-main:5432/agentgrouchotest`
  - Automatically cleaned up between tests

Key testing components:
- conftest.py: Provides shared test fixtures including:
  - Database session management
  - Test user creation  
  - FastAPI TestClient setup
- test_contents.py: Tests submission creation and SQS integration
- test_evaluations.py: Tests evaluation endpoints with mocked AI service

Run tests through Docker:
docker compose exec web pytest -v -s


Each test runs with a fresh database state, ensuring test isolation and reliability.

