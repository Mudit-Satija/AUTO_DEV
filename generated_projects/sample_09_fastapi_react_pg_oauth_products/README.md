# Project Overview

This is a full-stack application built with FastAPI as the backend, React as the frontend, PostgreSQL as the database, and OAuth for authentication.

## Features

- RESTful API endpoints powered by FastAPI
- React frontend with modern hooks and state management
- PostgreSQL database for persistent data storage
- OAuth 2.0 authentication for secure user access
- JWT-based session handling
- Environment-driven configuration

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- pip (Python package manager)
- npm or yarn

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-project-name.git
cd your-project-name
```

### 2. Set Up the Backend (FastAPI)

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory with the following content:

```
DATABASE_URL=postgresql://username:password@localhost:5432/project_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_AUTH_URL=https://auth-provider.com/oauth/authorize
OAUTH_TOKEN_URL=https://auth-provider.com/oauth/token
OAUTH_USER_INFO_URL=https://auth-provider.com/api/userinfo
```

Initialize the database:

```bash
python -m app.database init
```

Run the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`.

### 3. Set Up the Frontend (React)

Navigate to the frontend directory:

```bash
cd ../frontend
```

Install dependencies:

```bash
npm install
```

Create a `.env` file in the `frontend` directory:

```
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_OAUTH_CLIENT_ID=your-oauth-client-id
REACT_APP_OAUTH_AUTH_URL=https://auth-provider.com/oauth/authorize
```

Start the React development server:

```bash
npm start
```

The frontend will be available at `http://localhost:3000`.

### 4. Run Both Services

Ensure both servers are running:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

The frontend will automatically redirect to the OAuth provider for authentication. After successful login, the user will be redirected back to the frontend with an access token.

### 5. Database Schema

The PostgreSQL database will be automatically initialized with required tables on first run. The schema includes:

- `users`: Stores OAuth user information (id, email, name, oauth_provider, oauth_id, created_at)
- `tokens`: Stores refresh and access tokens (user_id, access_token, refresh_token, expires_at)

## API Documentation

The FastAPI backend includes auto-generated Swagger UI at:

`http://localhost:8000/docs`

## Testing

Run backend tests:

```bash
cd backend
pytest
```

Run frontend tests:

```bash
cd frontend
npm test
```

## Deployment

For production deployment:

- Use Gunicorn for the FastAPI backend
- Build the React app with `npm run build`
- Serve the React build folder via Nginx or similar
- Use environment variables for production secrets
- Enable HTTPS and secure headers

## License

MIT