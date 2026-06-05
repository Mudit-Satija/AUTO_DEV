# Project Overview

This is a full-stack application built with Express.js for the backend, React for the frontend, and MongoDB as the database. Authentication is handled via JWT. The backend includes three core modules: posts, inventory, and roles. The frontend features three pages: Dashboard, Posts, and Inventory.

## Features

- JWT-based authentication
- Protected routes for authenticated users
- Modular backend structure with posts, inventory, and roles
- React frontend with Dashboard, Posts, and Inventory pages
- MongoDB for data persistence using Mongoose

## Setup Instructions

### Prerequisites

- Node.js (v18+)
- MongoDB (local or cloud instance)
- npm or yarn

### Backend Setup

1. Navigate to the project root directory:
   ```bash
   cd project-root
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   npm install
   ```

3. Create a `.env` file in the `backend` directory with the following:
   ```
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/project-db
   JWT_SECRET=your-jwt-secret-key-here
   ```

4. Start the backend server:
   ```bash
   npm start
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the `frontend` directory:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```

### Database Setup

Ensure MongoDB is running. The backend connects to MongoDB using the URI specified in `.env`. Collections will be automatically created on first use.

### Authentication Flow

- Login endpoint: `POST /api/auth/login`
- Register endpoint: `POST /api/auth/register`
- Protected routes require a valid JWT token in the `Authorization` header:
  ```
  Authorization: Bearer <token>
  ```

### Project Structure

**Backend:**
- `app.js` – Express app configuration and route mounting
- `routes/` – Aggregated routes for auth, posts, inventory, roles
- `controllers/` – Route handlers
- `models/` – Mongoose schemas for posts, inventory, roles
- `middleware/` – Auth middleware and JWT verification
- `services/` – Business logic

**Frontend:**
- `src/pages/` – React components: Dashboard.jsx, Posts.jsx, Inventory.jsx
- `src/App.jsx` – Route configuration and auth protection
- `src/api/` – HTTP clients for backend calls
- `src/context/` – Auth context for JWT token management

### Running the App

1. Start MongoDB
2. Start backend: `cd backend && npm start`
3. Start frontend: `cd frontend && npm run dev`

Open http://localhost:5173 in your browser to access the application.

### Notes

- All routes under `/api` are protected by auth middleware except `/api/auth/login` and `/api/auth/register`.
- Tokens are stored in localStorage on the frontend and sent in headers for protected requests.
- Role-based access control is implemented in the backend via the roles module.