# Task Management System

A full-stack task management application built with Express.js, React, and MongoDB, featuring JWT-based authentication.

## Features

- User authentication with JWT
- Protected routes for Dashboard and Tasks pages
- RESTful API for task management
- MongoDB backend with Mongoose ODM
- React frontend with Vite

## Prerequisites

- Node.js (v18+)
- MongoDB (local or cloud)
- npm or yarn

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the `backend` folder:
   ```
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/taskmanager
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

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```

## Project Structure

### Backend
- `app.js` - Express app configuration and route mounting
- `routes/tasks.js` - Task-related API routes (protected by auth middleware)
- `models/Task.js` - Mongoose task schema
- `middleware/auth.js` - JWT authentication middleware
- `.env` - Environment variables

### Frontend
- `src/pages/Dashboard.jsx` - Dashboard page (authenticated)
- `src/pages/Tasks.jsx` - Tasks management page (authenticated)
- `src/App.jsx` - Main React component with routing
- `src/context/AuthContext.jsx` - JWT authentication context
- `src/api/index.js` - API client for backend requests

## Authentication

JWT authentication is enabled. All protected routes (Dashboard, Tasks) require a valid JWT token stored in localStorage after login. The backend verifies tokens via the `auth.js` middleware before allowing access to task routes.

## API Endpoints

- `POST /api/auth/login` - Login and get JWT token
- `GET /api/tasks` - Get all tasks (authenticated)
- `POST /api/tasks` - Create a new task (authenticated)
- `PUT /api/tasks/:id` - Update a task (authenticated)
- `DELETE /api/tasks/:id` - Delete a task (authenticated)

## Environment Variables

| Variable | Description |
|----------|-------------|
| PORT | Backend server port (default: 5000) |
| MONGODB_URI | MongoDB connection string |
| JWT_SECRET | Secret key for JWT signing |

## Running the App

1. Ensure MongoDB is running
2. Start backend: `cd backend && npm start`
3. Start frontend: `cd frontend && npm run dev`
4. Open http://localhost:5173 in your browser

## License

MIT