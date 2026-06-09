# Task Management System

A full-stack application built with Express.js, React, and MongoDB, featuring JWT-based authentication.

## Features

- User authentication with JWT
- Protected routes for Dashboard and Tasks
- MongoDB backend with Mongoose models for users and tasks
- React frontend with separate pages for Login, Dashboard, and Tasks
- Clean separation of concerns with modular Express routes

## Prerequisites

- Node.js (v18+)
- MongoDB (local or cloud instance)
- npm or yarn

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the `backend` directory:
   ```
   MONGO_URI=your_mongodb_connection_string
   JWT_SECRET=your_jwt_secret_key_here
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
- `config/db.js` - MongoDB connection setup
- `routes/users.js` - User authentication routes (login, register)
- `routes/tasks.js` - Task management routes (protected)
- `models/User.js` - Mongoose user schema
- `models/Task.js` - Mongoose task schema
- `middleware/auth.js` - JWT authentication middleware

### Frontend

- `src/pages/Login.jsx` - Login page component
- `src/pages/Dashboard.jsx` - Protected dashboard page
- `src/pages/Tasks.jsx` - Protected tasks management page
- `src/App.jsx` - Main React router configuration
- `src/context/AuthContext.jsx` - JWT authentication context

## Authentication

JWT authentication is enabled. The backend issues tokens upon successful login. All protected routes (tasks) require a valid JWT in the Authorization header. The frontend stores the token in localStorage and attaches it to requests automatically.

## Running the App

1. Ensure MongoDB is running
2. Start the backend server
3. Start the frontend server
4. Open http://localhost:5173 in your browser
5. Register or login to access the Dashboard and Tasks pages

## Environment Variables

Required in `.env` (backend):

- `MONGO_URI`: MongoDB connection string
- `JWT_SECRET`: Secret key for signing JWT tokens

## Dependencies

### Backend
- express
- mongoose
- dotenv
- jsonwebtoken
- bcryptjs

### Frontend
- react
- react-dom
- react-router-dom
- axios
