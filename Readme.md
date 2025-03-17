# Deployment Plan Generator

A FastAPI-based application for automated deployment planning and analysis.

## Requirements

### Jenkins Plugins

- Role-based Authorization Strategy
- Pipeline: REST API
- Pipeline: Stage View

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB
- Node.js (for frontend components, if applicable)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/int-deplora-plan-gen.git
   cd int-deplora-plan-gen
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (create a `.env` file):
   ```
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=deployment_db
   LOG_LEVEL=INFO
   ```

## Running the Application

### Start the server

```bash
uvicorn main:app
```

The API will be available at: http://localhost:8000

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage Guide

### Analyzing a Repository

Send a POST request to `/api/analyze` with the repository details.

### Managing Deployment Plans

Use the available endpoints under `/api/management` to create, retrieve, and update deployment plans.

### Working with the Chat Interface

The chat API is available at `/api/chat` for interactive deployment planning.

## Project Structure

- `api/`: API endpoints
- `core/`: Core configurations and utilities
- `services/`: Business logic services
- `resources/`: Templates and configuration files
- `models/`: Data models
