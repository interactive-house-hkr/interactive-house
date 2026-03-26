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

1. Create and activate a virtual environment.
2. From the repo root, install the Python packages:
   ```powershell
   .\services\scripts\setup.ps1
   ```
3. Create a `services/.env` file based on `services/.env.example`.
4. Download the Firebase service account JSON and place it in `services/src/config/`.

## .env values

The server reads its local settings from `services/.env`.

Use `services/.env.example` as a starting point.

### Server configuration

- `HOST`: which address the server should bind to locally. `0.0.0.0` is fine for normal development.
- `PORT`: which port the FastAPI server should run on.
- `LOG_LEVEL`: log level for local debugging, for example `INFO`.

### API configuration

- `API_KEY`: this is the server's own API setting, not a Firebase API key. In the current code it is only loaded from settings and is not heavily used in the request flow yet, so a simple local dev value is enough.
- `DEVICE_TIMEOUT_SECONDS`: how long a device can go without updates before it is treated as offline.

### Firebase configuration

- `FIREBASE_PROJECT_ID`: your Firebase project ID.
- `FIREBASE_SERVICE_ACCOUNT`: the filename or path to the Firebase service account JSON used by the server.
  Example:
  `serviceAccountKey.json`
- `FIREBASE_DATABASE_URL`: the Firebase Realtime Database URL for the project.

The Firebase service account JSON file should be placed in:
`services/src/config/`

### Auth configuration

- `SECRET_KEY`: used by the server to sign JWT tokens in the auth code. Right now this mostly matters for startup and auth-related code paths, so for local development a simple dev value is enough.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: how long an access token should be valid when auth tokens are created.
- `REFRESH_TOKEN_EXPIRE_DAYS`: how long a refresh token should be valid when auth tokens are created.

## Running the Server

From the repo root:

Normal start:
```powershell
.\services\scripts\dev-server.ps1
```

Start without bridge:
```powershell
.\services\scripts\dev-server.ps1 -DisableBridge
```

### Why run without bridge?

Normally, the server starts the BLE/USB bridge on startup and tries to connect to a physical device.

Running with `-DisableBridge` is useful when:
- you are working on the API only
- you do not have the Arduino/device hardware available
- you want cleaner logs without BLE/USB connection retries

## API Documentation

When the server is running, API documentation is available at:
http://localhost:8000/docs

## Notes
- The server is the single source of truth for the system
- Devices and user interfaces do not communicate directly
- All communication is done through the REST API
