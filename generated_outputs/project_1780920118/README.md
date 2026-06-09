# Task Management System

A simple task management application built with Express.js for the backend and React for the frontend, using MongoDB as the database. Authentication is disabled.

## Features

- View and manage pending tasks
- View and manage completed tasks
- MongoDB-backed task storage
- RESTful API endpoints for task operations

## Prerequisites

- Node.js (v18 or higher)
- MongoDB (local or cloud instance)
- npm or yarn

## Setup Instructions

### Backend Setup

1. Navigate to the project root directory:
   ```
   cd backend
   ```

2. Install backend dependencies:
   ```
   npm install
   ```

3. Create a `.env` file in the `backend` directory and set your MongoDB connection string:
   ```
   MONGO_URI=mongodb://localhost:27017/taskdb
   ```

4. Start the Express server:
   ```
   npm start
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install frontend dependencies:
   ```
   npm install
   ```

3. Start the React development server:
   ```
   npm run dev
   ```

## Directory Structure

### Backend
- `app.js` - Express app configuration and route mounting
- `routes/tasks.js` - Task-related API routes
- `models/Task.js` - Mongoose task schema
- `config/db.js` - MongoDB connection setup

### Frontend
- `src/pages/pending-tasks.jsx` - Component to display pending tasks
- `src/pages/completed-tasks.jsx` - Component to display completed tasks
- `src/App.jsx` - Main React router configuration
- `src/main.jsx` - Entry point for React app

## API Endpoints

- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/pending` - Get all pending tasks
- `GET /api/tasks/completed` - Get all completed tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/:id` - Update a task by ID
- `DELETE /api/tasks/:id` - Delete a task by ID

## Database Schema

The `Task` model has the following fields:
- `title` (string, required)
- `description` (string)
- `status` (string, enum: 'pending', 'completed', default: 'pending')
- `createdAt` (date, default: Date.now)
- `updatedAt` (date, default: Date.now)

## Running the Application

1. Ensure MongoDB is running.
2. Start the backend server: `npm start` in the `backend` directory.
3. Start the frontend server: `npm run dev` in the `frontend` directory.
4. Open http://localhost:5173 in your browser to access the frontend.

## Notes

- No authentication is implemented or required.
- All routes are publicly accessible.
- The frontend communicates with the backend via HTTP requests to `/api/` endpoints.