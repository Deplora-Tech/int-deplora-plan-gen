FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including build tools for psycopg2 and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    gnupg \
    git \
    wget \
    openjdk-17-jdk \
    lsb-release \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    redis-server \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Jenkins
RUN wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | apt-key add - \
    && sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list' \
    && apt-get update && apt-get install -y jenkins \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright dependencies
RUN pip install playwright && playwright install --with-deps chromium

# Copy application code
COPY . .

# Create directories for repos if they don't exist
RUN mkdir -p /app/repo-clones /app/temp-repos

# Set environment variables for directories
ENV REPO_PATH=/app/repo-clones \
    TEMP_REPO_PATH=/app/temp-repos

# Expose ports for the API, Jenkins, and Redis
EXPOSE 80

# Create startup script to run services
RUN echo '#!/bin/bash\n\
service jenkins start\n\
service redis-server start\n\
echo "Jenkins and Redis services started"\n\
uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Command to run the startup script
CMD uvicorn main:app --host 0.0.0.0 --loop asyncio --port 80
