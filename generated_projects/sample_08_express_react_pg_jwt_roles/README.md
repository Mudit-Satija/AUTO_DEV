# Project Overview

This is a full-stack application built with Express.js (backend), React (frontend), PostgreSQL (database), and JWT for authentication. The backend provides a RESTful API for managing workspaces, projects, and tasks with role-based access control. All database interactions use raw SQL via the `pg` library without any ORM.

## Features

- User registration and login with JWT token issuance
- Protected routes for workspaces, projects, and tasks
- PostgreSQL database with normalized schema
- CORS enabled for React frontend communication
- Environment variable configuration via dotenv
- Modular route structure with centralized auth middleware

## Prerequisites

- Node.js (v18+ recommended)
- PostgreSQL (v12+ recommended)
- npm or yarn

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Set Up Database

Create a PostgreSQL database named `project_db`:

```bash
createdb project_db
```

Create the required tables by running the following SQL in your database:

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE workspaces (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(150) NOT NULL,
  description TEXT,
  status VARCHAR(20) DEFAULT 'todo',
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  assigned_to INTEGER REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
PORT=5000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=project_db
DB_USER=your_db_username
DB_PASSWORD=your_db_password
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRES_IN=24h
```

Replace placeholders with your actual database credentials and a secure JWT secret.

### 5. Start the Backend Server

```bash
npm start
```

The server will run on `http://localhost:5000`.

### 6. Start the React Frontend

Navigate to the frontend directory (if separate) and run:

```bash
cd frontend
npm install
npm start
```

The React app will run on `http://localhost:3000`.

## API Endpoints

### Auth

- `POST /api/auth/register` — Register a new user
- `POST /api/auth/login` — Login and receive JWT token

### Protected Routes (require Authorization header with Bearer JWT)

- `GET /api/workspaces` — List all workspaces
- `POST /api/workspaces` — Create a new workspace
- `GET /api/workspaces/:id` — Get a specific workspace
- `PUT /api/workspaces/:id` — Update a workspace
- `DELETE /api/workspaces/:id` — Delete a workspace

- `GET /api/projects` — List all projects
- `POST /api/projects` — Create a new project
- `GET /api/projects/:id` — Get a specific project
- `PUT /api/projects/:id` — Update a project
- `DELETE /api/projects/:id` — Delete a project

- `GET /api/tasks` — List all tasks
- `POST /api/tasks` — Create a new task
- `GET /api/tasks/:id` — Get a specific task
- `PUT /api/tasks/:id` — Update a task
- `DELETE /api/tasks/:id` — Delete a task

## Folder Structure

```
/
├── config/
│   └── database.js
├── controllers/
│   ├── authController.js
│   ├── workspaceController.js
│   ├── projectController.js
│   └── taskController.js
├── models/
│   ├── authModel.js
│   ├── workspaceModel.js
│   ├── projectModel.js
│   └── taskModel.js
├── routes/
│   ├── index.js
│   ├── auth.js
│   ├── workspaces.js
│   ├── projects.js
│   └── tasks.js
├── middleware/
│   └── auth.js
├── app.js
├── package.json
├── .env
└── README.md
```

## Authentication Flow

1. User registers or logs in via `/api/auth/register` or `/api/auth/login`
2. Server validates credentials and returns a JWT token
3. Frontend stores the token (e.g., in localStorage)
4. For protected requests, frontend includes the token in the `Authorization` header: `Bearer <token>`
5. Server verifies JWT via middleware before allowing access to workspace/project/task routes

## Dependencies

- express
- pg
- dotenv
- jsonwebtoken
- cors
- bcrypt

## License

MIT