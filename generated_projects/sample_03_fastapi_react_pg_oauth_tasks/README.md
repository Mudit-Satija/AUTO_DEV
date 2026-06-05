# Project Overview

This is a full-stack application built with FastAPI as the backend, React as the frontend, PostgreSQL as the database, and OAuth for authentication.

## Features

- FastAPI backend with RESTful endpoints
- React frontend with modern hooks and state management
- PostgreSQL database for persistent data storage
- OAuth 2.0 authentication (supports Google, GitHub, etc.)
- JWT-based session management
- CORS-enabled for seamless frontend-backend communication
- Environment-based configuration (development, production)

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- pip
- npm or yarn

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
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

Initialize the database:

```bash
python -m app.database.init_db
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

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_GITHUB_CLIENT_ID=your-github-client-id
```

Start the React development server:

```bash
npm start
```

The frontend will be available at `http://localhost:3000`.

### 4. Access the Application

Open your browser and navigate to `http://localhost:3000`.

You can now authenticate using Google or GitHub OAuth, and interact with the protected API endpoints.

## Directory Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── init_db.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── oauth.py
│   │   │   └── tokens.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── users.py
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── services/
    │   ├── App.js
    │   └── index.js
    ├── .env
    ├── package.json
    └── README.md
```

## Environment Variables

Ensure all required environment variables are set in both `backend/.env` and `frontend/.env`. Missing or incorrect values will prevent authentication and database connectivity.

## License

This project is licensed under the MIT License.