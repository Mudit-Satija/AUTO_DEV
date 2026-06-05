# Project Overview

This is a full-stack application built with Express.js for the backend and React for the frontend, using PostgreSQL as the database and JWT for authentication. The system manages workspaces, projects, and tasks with protected routes requiring valid JWT tokens.

## Backend Structure

- **Workspaces**: Manage organizational workspaces
- **Projects**: Track projects within workspaces
- **Tasks**: Manage tasks assigned to projects

## Frontend Structure

- **Login**: Authentication page for users
- **Dashboard**: Main view after login showing workspaces and projects
- **Settings**: User preferences and account settings

## Prerequisites

- Node.js (v18+)
- PostgreSQL (v14+)
- npm or yarn

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Install Backend Dependencies

```bash
cd backend
npm install
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Set Up PostgreSQL Database

Create a new database named `project_db`:

```bash
createdb project_db
```

Create a `.env` file in the `backend` directory:

```
PORT=5000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=project_db
DB_USER=postgres
DB_PASSWORD=yourpassword
JWT_SECRET=your-jwt-secret-key-here
JWT_EXPIRES_IN=7d
```

### 5. Run Database Migrations

Create the required tables using the following SQL:

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE workspaces (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  assigned_to INTEGER REFERENCES users(id),
  status VARCHAR(50) DEFAULT 'todo',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 6. Start the Backend Server

```bash
cd backend
npm start
```

The backend will run on `http://localhost:5000`.

### 7. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### 8. Usage

- Navigate to `http://localhost:5173/login` to log in
- After successful login, you will be redirected to the Dashboard
- Use Settings to update your profile or change preferences

## Authentication

JWT tokens are issued upon successful login and must be included in the `Authorization` header for protected routes:

```
Authorization: Bearer <your-jwt-token>
```

Protected routes include:
- `/api/workspaces/*`
- `/api/projects/*`
- `/api/tasks/*`

Public routes:
- `/api/auth/login`
- `/api/auth/register`

## Folder Structure

```
project/
├── backend/
│   ├── app.js
│   ├── routes/
│   │   ├── auth.js
│   │   ├── workspaces.js
│   │   ├── projects.js
│   │   └── tasks.js
│   ├── controllers/
│   │   ├── authController.js
│   │   ├── workspaceController.js
│   │   ├── projectController.js
│   │   └── taskController.js
│   ├── models/
│   │   ├── user.js
│   │   ├── workspace.js
│   │   ├── project.js
│   │   └── task.js
│   ├── middleware/
│   │   └── auth.js
│   ├── .env
│   └── package.json
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── Dashboard.jsx
    │   │   └── Settings.jsx
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── vite.config.js
    └── package.json
```

## Environment Variables

Ensure the following environment variables are set in `backend/.env`:

- `PORT` — backend server port (default: 5000)
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` — PostgreSQL connection details
- `JWT_SECRET` — secret key for signing JWT tokens
- `JWT_EXPIRES_IN` — token expiration time (e.g., 7d)

## Testing

Use tools like Postman or curl to test API endpoints. For example:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Use the returned token in subsequent requests:

```bash
curl -X GET http://localhost:5000/api/workspaces \
  -H "Authorization: Bearer <token>"
```

## License

MIT