# Task Management System

A full-stack application built with Express.js, React, and MongoDB, featuring JWT-based authentication.

## Features

- User authentication with JWT
- Protected routes for Dashboard and Tasks
- MongoDB backend with Mongoose models
- Modular Express.js structure with separate routes for users and tasks
- React frontend with page-based routing

## Prerequisites

- Node.js (v18+)
- MongoDB (local or cloud instance)
- npm or yarn

## Backend Setup

1. Install dependencies:

   ```bash
   cd backend
   npm install
   ```

2. Create a `.env` file in the `backend` directory:

   ```
   MONGODB_URI=mongodb://localhost:27017/taskmanager
   JWT_SECRET=your_jwt_secret_key_here
   PORT=5000
   ```

3. Start the backend server:

   ```bash
   npm start
   ```

## Frontend Setup

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Start the frontend development server:

   ```bash
   npm run dev
   ```

## Project Structure

### Backend

- `app.js` - Express app configuration and MongoDB connection
- `routes/` - Route handlers for users and tasks
- `models/` - Mongoose schemas for User and Task
- `middleware/auth.js` - JWT authentication middleware
- `.env` - Environment variables

### Frontend

- `src/pages/` - React components: Dashboard.jsx, Tasks.jsx, Login.jsx
- `src/App.jsx` - Router configuration
- `src/main.jsx` - React root entry point
- `src/services/api.js` - HTTP client for API calls

## Authentication Flow

1. User logs in via Login page → POST `/api/users/login`
2. Server validates credentials and returns JWT token
3. Token is stored in localStorage
4. Subsequent requests include Authorization header: `Bearer <token>`
5. Protected routes (Dashboard, Tasks) verify token via auth middleware

## Database Models

### User
- email (String, unique)
- password (String)
- createdAt (Date)

### Task
- title (String)
- description (String)
- completed (Boolean)
- userId (ObjectId, ref: User)
- createdAt (Date)

## API Endpoints

### Public
- `POST /api/users/login` - Authenticate user and return JWT
- `POST /api/users/register` - Create new user

### Protected (requires JWT)
- `GET /api/tasks` - List all tasks for authenticated user
- `POST /api/tasks` - Create new task
- `GET /api/tasks/:id` - Get specific task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `GET /api/users/me` - Get current user profile

## Environment Variables

| Variable | Description |
|----------|-------------|
| MONGODB_URI | MongoDB connection string |
| JWT_SECRET | Secret key for JWT signing |
| PORT | Backend server port |

## Deployment

Build the frontend:

```bash
cd frontend
npm run build
```

Serve the static files from Express:

```js
// In app.js, after all API routes
app.use(express.static(path.join(__dirname, '../frontend/dist')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/dist/index.html'));
});
```

Then deploy the backend as a Node.js application.

## License

MIT