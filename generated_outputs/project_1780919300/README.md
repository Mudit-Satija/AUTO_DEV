# Task Management System

A full-stack application built with Express.js, React, and MongoDB, featuring JWT-based authentication.

## Features

- User authentication with JWT
- Protected routes for Dashboard and Tasks
- MongoDB backend with Mongoose models for users and tasks
- React frontend with SPA routing
- Clean separation of concerns between frontend and backend

## Prerequisites

- Node.js (v18 or higher)
- MongoDB (local or cloud instance)
- npm or yarn

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file in the backend root with the following:
   ```
   MONGODB_URI=mongodb://localhost:27017/taskmanager
   JWT_SECRET=your_jwt_secret_key_here
   PORT=5000
   ```

4. Start the backend server:
   ```
   npm start
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file in the frontend root with:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

4. Start the frontend development server:
   ```
   npm run dev
   ```

## Project Structure

### Backend
- `app.js` - Express app configuration and route mounting
- `routes/` - API route handlers
  - `auth.js` - Public auth routes (login, register)
  - `tasks.js` - Protected task routes
  - `users.js` - Protected user routes
  - `index.js` - Aggregates all API routes
- `models/` - Mongoose schemas
  - `User.js`
  - `Task.js`
- `middleware/` - Authentication middleware
  - `auth.js`
- `services/` - Business logic
  - `authService.js`
  - `taskService.js`
  - `userService.js`

### Frontend
- `src/`
  - `pages/`
    - `Dashboard.jsx` - Protected dashboard view
    - `Tasks.jsx` - Protected tasks management view
    - `Login.jsx` - Public login view
  - `components/` - Reusable UI components
  - `services/` - API service wrappers
  - `context/` - Auth context provider
  - `App.jsx` - Main router
  - `main.jsx` - Entry point

## Authentication Flow

1. User logs in via `/api/auth/login`
2. Server validates credentials and returns JWT in response
3. Client stores JWT in localStorage
4. Subsequent requests include JWT in Authorization header
5. Protected routes verify token using auth middleware before processing

## Database Models

### User Schema
- username (String, required, unique)
- email (String, required, unique)
- password (String, required)
- createdAt (Date)

### Task Schema
- title (String, required)
- description (String)
- status (String, enum: 'todo', 'in-progress', 'done', default: 'todo')
- userId (ObjectId, ref: 'User', required)
- createdAt (Date)
- updatedAt (Date)

## API Endpoints

### Public
- POST /api/auth/login - Authenticate user and return JWT
- POST /api/auth/register - Create new user

### Protected (requires valid JWT)
- GET /api/tasks - Get all tasks for authenticated user
- POST /api/tasks - Create new task
- GET /api/tasks/:id - Get specific task
- PUT /api/tasks/:id - Update task
- DELETE /api/tasks/:id - Delete task
- GET /api/users/me - Get current user profile

## Running Tests

To run tests, install Jest and run:
```
npm test
```

## Deployment

Build the frontend for production:
```
npm run build
```

Serve the static files from the `dist` folder using Express or a static server.

## License

MIT