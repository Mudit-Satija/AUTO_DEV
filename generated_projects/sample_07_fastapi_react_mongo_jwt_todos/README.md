# FastAPI + React + MongoDB + JWT Project

This is a full-stack web application built with FastAPI as the backend, React as the frontend, MongoDB as the database, and JWT for authentication.

## Project Structure

- Backend: FastAPI (Python) running on port 8000
- Frontend: React (JavaScript) running on port 3000
- Database: MongoDB (local or remote instance)
- Authentication: JWT tokens for secure user sessions

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- MongoDB installed and running (or access to a MongoDB Atlas cluster)

## Setup Instructions

### 1. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables (create a `.env` file in the backend folder):

```env
SECRET_KEY=your-secure-jwt-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=your_db_name
```

Run the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`.

### 2. Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install JavaScript dependencies:

```bash
npm install
```

Set environment variables (create a `.env` file in the frontend folder):

```env
REACT_APP_API_URL=http://localhost:8000
```

Start the React development server:

```bash
npm start
```

The frontend will be available at `http://localhost:3000`.

### 3. Database Setup

Ensure MongoDB is running. If using MongoDB Atlas, update the `MONGODB_URL` in the `.env` file to your Atlas connection string.

Create a database and collection as needed. The backend will automatically create collections on first use.

## Authentication Flow

1. User registers via `/auth/register` endpoint (POST).
2. User logs in via `/auth/login` endpoint (POST) with email and password.
3. Server returns a JWT access token and refresh token (if implemented).
4. Frontend stores the access token in memory or localStorage.
5. Each protected API request includes the token in the Authorization header: `Bearer <token>`.
6. Backend validates the token and returns protected data or 401 if invalid.

## API Endpoints (Backend)

- `POST /auth/register` — Register a new user
- `POST /auth/login` — Log in and get JWT token
- `GET /users/me` — Get current user profile (protected)
- `GET /items` — List all items (protected)
- `POST /items` — Create a new item (protected)

## Frontend Features

- Login and registration forms
- Protected routes (dashboard, profile)
- Token refresh mechanism (optional)
- HTTP interceptors to attach JWT tokens
- Error handling for 401 and 500 responses

## Deployment

For production:

- Use Gunicorn or Uvicorn with workers for the backend.
- Build the React app: `npm run build` and serve with a static server (e.g., Nginx).
- Use environment variables for secrets and database URLs.
- Enable HTTPS.
- Set proper CORS headers in FastAPI.

## License

MIT