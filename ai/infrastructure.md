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

Docker commands:
  docker compose up -d
  docker compose down
  docker compose build
  docker compose exec fastapi alembic upgrade head

Connecting via docker:
  docker exec -it postgres-main psql -U postgres -d agentgroucho

View logs:
  docker compose logs -f fastapi

Migrations:
Using Alembic
Generate migrations in docker:
  docker exec -it groucho-api alembic revision --autogenerate -m "First migration"
Run migrations through Docker:
  docker exec -it groucho-api alembic upgrade head

The database connection string in the app uses the Docker network name:
  DATABASE_URL = "postgresql://postgres:postgres@postgres-main:5432/agentgroucho"

# Deployment

- The backend API is deployed on AWS Lambda, allowing for serverless execution and scalability.
- The API communicates with mutliple SvelteKit frontends over HTTPS, with the frontends making requests to the Lambda function.

# Testing

The test suite uses pytest with a dedicated test database:
- Test Database:
  - Name: agentgroucho
  - Connection: `postgresql://postgres:postgres@postgres-main:5432/agentgroucho_test`
  - Automatically cleaned up between tests

Key testing components:
- conftest.py: Provides shared test fixtures including:
  - Database session management
  - Test user creation
  - Test submission creation
  - FastAPI TestClient setup
- test_contents.py: Tests submission creation and SQS integration
- test_evaluations.py: Tests evaluation endpoints with mocked AI service

Run tests through Docker:
docker compose exec web pytest -v -s


Each test runs with a fresh database state, ensuring test isolation and reliability.

# Local Lambda Testing

To test the Lambda function locally using SAM CLI: 1. 

Ensure Docker context is set correctly: 
`docker context use desktop-linux` 

2. Run SAM locally: 
`DOCKER_HOST="unix:///Users/lucasweaver/.docker/run/docker.sock" sam local start-api --template template.yaml`

Note: For convenience, add these lines to your `~/.zshrc`: `docker context use desktop-linux > /dev/null 2>&1` and `export DOCKER_HOST="unix:///Users/lucasweaver/.docker/run/docker.sock"`. 

This allows testing the full Lambda function locally, including SQS message processing from LocalStack.

# LocalStack Integration

- LocalStack Container:
  - Service: localstack
  - Container: groucho-localstack
  - Port: 4566
  - Region: us-west-2
  - Services: SQS

SQS Queue Details:
- Queue Name: groucho-task-queue
- URL Format: http://localstack:4566/000000000000/groucho-task-queue
- Test Credentials:
  - AWS_ACCESS_KEY_ID: test
  - AWS_SECRET_ACCESS_KEY: test

LocalStack Commands:
```bash
# List queues
docker exec groucho-localstack awslocal sqs list-queues

# Create queue
docker exec groucho-localstack awslocal sqs create-queue --queue-name groucho-task-queue --region us-west-2

# Delete queue
docker exec groucho-localstack awslocal sqs delete-queue --queue-url http://localhost:4566/000000000000/groucho-task-queue

# View queue attributes
docker exec groucho-localstack awslocal sqs get-queue-attributes \
    --queue-url http://localhost:4566/000000000000/groucho-task-queue \
    --attribute-names All
```