FROM public.ecr.aws/docker/library/python:3.12-slim

# Copy the Lambda Web Adapter
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

# Set environment variables
ENV PORT=8020
ENV AWS_LAMBDA_EXEC_WRAPPER=/opt/extensions/lambda-adapter
ENV PYTHONUNBUFFERED=1
# Optimize Python bytecode compilation
ENV PYTHONOPTIMIZE=2
# Disable bytecode writing to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Set a fixed hash seed for reproducible builds
ENV PYTHONHASHSEED=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/task

# Copy requirements first for better caching
COPY requirements.txt .
# Install dependencies with optimizations
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code, alembic files, and seeds
COPY ./app ./app
COPY alembic.ini .
COPY alembic ./alembic
# COPY ./seeds ./seeds

# Pre-compile Python code
RUN python -m compileall ./app

# If migrations are needed
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8020 --workers 1 --no-access-log --log-level warning

# If not
# CMD uvicorn app.main:app --host 0.0.0.0 --port 8020 --workers 1 --no-access-log --log-level warning