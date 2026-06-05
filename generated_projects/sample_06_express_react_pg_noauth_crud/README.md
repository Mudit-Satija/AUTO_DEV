# Project Overview

This is a full-stack application built with Express.js (backend), React (frontend), and PostgreSQL (database). Authentication is handled via JWT tokens, and all database interactions use raw SQL queries with the `pg` library. The backend exposes a RESTful API under `/api`, and the frontend is designed to consume it.

## Features

- User registration and login with JWT authentication
- Protected routes for workspaces, projects, and tasks
- Raw SQL queries via `pg.Pool` (no ORM)
- CORS enabled for frontend communication
- Environment variables managed with `dotenv`

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

### 2. Install Dependencies

```bash
npm install
```

### 3. Set Up PostgreSQL

Create a new database named `project_db`:

```bash
createdb project_db
```

Create a user (or use your preferred user):

```bash
createuser -P project_user
```

Grant permissions:

```sql
psql -U postgres
> GRANT ALL PRIVILEGES ON DATABASE project_db TO project_user;
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
PORT=5000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=project_db
DB_USER=project_user
DB_PASSWORD=your_password
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRES_IN=24h
```

### 5. Run Database Migrations

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

### 6. Start the Backend Server

```bash
npm start
```

The backend will run on `http://localhost:5000`.

### 7. Start the Frontend (React)

Navigate to the frontend directory (if separate) and run:

```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000`.

## API Endpoints

### Auth

- `POST /api/auth/register` — Register a new user
- `POST /api/auth/login` — Log in and receive JWT token

### Protected Routes (require JWT in Authorization header)

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
├── routes/
│   ├── index.js
│   ├── auth.js
│   ├── workspaces.js
│   ├── projects.js
│   └── tasks.js
├── controllers/
│   ├── authController.js
│   ├── workspaceController.js
│   ├── projectController.js
│   └── taskController.js
├── models/
│   ├── user.js
│   ├── workspace.js
│   ├── project.js
│   └── task.js
├── middleware/
│   └── auth.js
├── app.js
├── package.json
├── .env
└── README.md
```

## Dependencies

- express
- pg
- dotenv
- jsonwebtoken
- cors
- bcrypt

## License

MIT