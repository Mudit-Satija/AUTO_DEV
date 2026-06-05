# FastAPI + Vue + PostgreSQL JWT Auth Project

A full-stack web application using FastAPI as the backend, Vue.js as the frontend, PostgreSQL as the database, and JWT for authentication.

## Features

- FastAPI backend with RESTful endpoints
- Vue.js frontend with Vuex and Vue Router
- PostgreSQL database with SQLAlchemy ORM
- JWT-based authentication (login, logout, token refresh)
- Environment-based configuration
- CORS support for frontend-backend communication
- Dockerized deployment ready

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker (optional, for containerized deployment)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/your-project-name.git
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

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Initialize the database:

```bash
python -m app.database.init_db
```

Run the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Set Up the Frontend (Vue)

Navigate to the frontend directory:

```bash
cd ../frontend
```

Install dependencies:

```bash
npm install
```

Create a `.env` file in the `frontend` directory:

```env
VUE_APP_API_BASE_URL=http://localhost:8000/api
```

Run the Vue development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Database Setup (PostgreSQL)

Ensure PostgreSQL is running and create the database:

```bash
createdb your_db_name
```

Create a database user if needed:

```sql
CREATE USER username WITH PASSWORD 'password';
ALTER USER username CREATEDB;
```

Grant privileges:

```sql
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO username;
```

### 5. (Optional) Docker Deployment

Build and run the entire stack using Docker Compose:

```bash
docker-compose up --build
```

Access the frontend at `http://localhost:8080` and the API at `http://localhost:8000/api`

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── auth/            # Authentication routes and logic
│   │   ├── database/        # Database models and session
│   │   ├── schemas/         # Pydantic models
│   │   ├── models/          # SQLAlchemy models
│   │   └── utils/           # Helper functions (JWT, etc.)
│   ├── requirements.txt
│   └── .env
├── frontend/                # Vue.js frontend
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/          # Vue Router
│   │   ├── store/           # Vuex store
│   │   ├── views/
│   │   ├── api/             # HTTP client to backend
│   │   └── main.js
│   ├── public/
│   ├── .env
│   └── package.json
├── docker-compose.yml       # Docker orchestration
├── README.md
└── .gitignore
```

## API Endpoints

- `POST /api/auth/login` — Authenticate user and return tokens
- `POST /api/auth/refresh` — Refresh access token using refresh token
- `POST /api/auth/logout` — Invalidate refresh token
- `GET /api/users/me` — Get current user info (authenticated)
- `GET /api/users` — List all users (admin only)

## License

MIT License