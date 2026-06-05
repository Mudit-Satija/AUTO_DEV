# Project Overview

This is a full-stack application built with Express.js for the backend, React for the frontend, and MongoDB as the database. Authentication is handled via JWT. The system includes three backend modules: posts, inventory, and roles. The frontend features three pages: Dashboard, Posts, and Inventory.

## Features

- JWT-based authentication
- Protected routes for authenticated users
- RESTful API endpoints for posts, inventory, and roles
- React frontend with Dashboard, Posts, and Inventory pages
- MongoDB for data persistence using Mongoose

## Backend Setup

1. Install dependencies:
   ```
   cd backend
   npm install
   ```

2. Create a `.env` file in the `backend` directory:
   ```
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/projectdb
   JWT_SECRET=your_jwt_secret_key_here
   ```

3. Start the backend server:
   ```
   npm start
   ```

## Frontend Setup

1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

## Directory Structure

### Backend
- `app.js` — Main Express application with route mounting and auth middleware
- `routes/` — Contains route handlers for auth, posts, inventory, and roles
- `controllers/` — Business logic for each module
- `models/` — Mongoose schemas for posts, inventory, roles, and users
- `middleware/` — Auth middleware for JWT verification
- `services/` — Utility services for authentication and data handling

### Frontend
- `src/`
  - `pages/` — React components: Dashboard.jsx, Posts.jsx, Inventory.jsx
  - `App.jsx` — Main router with protected routes
  - `context/AuthContext.jsx` — Manages JWT token and user state
  - `api/` — Axios instances for API calls to backend

## Authentication Flow

1. User logs in via `/api/auth/login` — receives JWT token
2. Token is stored in localStorage
3. Each subsequent request includes the token in the Authorization header
4. Auth middleware verifies token before allowing access to protected routes
5. Protected routes: `/api/posts/*`, `/api/inventory/*`, `/api/roles/*`

## Environment Variables

Required in `.env` (backend):
- `PORT` — Server port (default: 5000)
- `MONGODB_URI` — MongoDB connection string
- `JWT_SECRET` — Secret key for JWT signing

## Testing

Run backend tests:
```
npm test
```

Run frontend tests:
```
npm test
```

## Deployment

Build frontend:
```
cd frontend
npm run build
```

Serve static files from Express:
- Copy `frontend/dist` contents to `backend/public`
- Ensure Express serves static files from `/public`

## Dependencies

### Backend
- express
- mongoose
- jsonwebtoken
- dotenv
- cors

### Frontend
- react
- react-dom
- react-router-dom
- axios
- context-api
- vite

## Notes

- All routes under `/api` are protected by auth middleware except `/api/auth/login` and `/api/auth/register`
- Roles are used to enforce access control on inventory and posts
- Database collections: `posts`, `inventory`, `roles`, `users`
- Frontend pages are lazy-loaded for performance