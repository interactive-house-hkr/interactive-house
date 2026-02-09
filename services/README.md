# services/

Server/API and DB assets live here (migrations, seeds, etc.).

## Technology
- Python
- FastAPI
- Firebase Realtime Database

## Project Structure
src/
  config/        Configuration and environment setup
  routes/        API endpoints
  controllers/   Request handling
  services/      Business logic
  models/        Domain models
  schemas/       API schemas (request/response)
  firebase/      Firebase data access layer

## Setup

1. Create and activate a virtual environment
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Download the Firebase service account JSON and place it in src/config/
4. Create a .env file based on .env.example

## Running the Server

From the repo root:
```
uvicorn services.src.main:app --reload
```

## API Documentation

When the server is running, API documentation is available at:
http://localhost:8000/docs

## Notes
- The server is the single source of truth for the system
- Devices and user interfaces do not communicate directly
- All communication is done through the REST API
