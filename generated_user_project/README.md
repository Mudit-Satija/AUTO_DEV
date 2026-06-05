# Project Overview

This is a full-stack application built with Express.js for the backend, React for the frontend, and MongoDB as the database. Authentication is handled via JWT. The backend includes three core modules: posts, inventory, and roles. The frontend includes three pages: Dashboard, Posts, and Inventory.

## Features

- JWT-based authentication
- Protected routes for authenticated users
- MongoDB data modeling with Mongoose
- Modular Express.js backend with route aggregation
- React frontend with Vite
- Role-based access control via roles module

## Backend Setup

1. Install dependencies:
   ```
   cd backend
   npm install express mongoose dotenv cors helmet morgan jsonwebtoken bcryptjs
   ```

2. Create a `.env` file in the `backend` directory:
   ```
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/projectdb
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
   npm install react react-dom react-router-dom axios
   ```

2. Start the frontend development server:
   ```
   npm run dev
   ```

## Directory Structure

### Backend
```
backend/
├── app.js
├── routes/
│   ├── index.js
│   ├── auth.js
│   ├── posts.js
│   ├── inventory.js
│   └── roles.js
├── models/
│   ├── Post.js
│   ├── InventoryItem.js
│   └── Role.js
├── middleware/
│   └── auth.js
└── .env
```

### Frontend
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Posts.jsx
│   │   └── Inventory.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── api/
│       └── index.js
└── vite.config.js
```

## Authentication Flow

1. User logs in via `/api/auth/login` → receives JWT token
2. Token is stored in localStorage or HTTP-only cookie
3. All subsequent requests include the token in the Authorization header: `Bearer <token>`
4. Protected routes (`/api/posts`, `/api/inventory`, `/api/roles`) use the `auth` middleware to verify token
5. Roles are checked within module handlers to enforce permissions

## Environment Variables

Ensure the following variables are set in `.env`:

- `PORT`: Backend server port (default: 5000)
- `MONGO_URI`: MongoDB connection string
- `JWT_SECRET`: Secret key for signing JWT tokens

## Running the Application

1. Start MongoDB locally or connect to a cloud instance
2. Start backend server: `cd backend && npm start`
3. Start frontend server: `cd frontend && npm run dev`
4. Open http://localhost:5173 in your browser

## Notes

- All backend routes are mounted under `/api`
- Auth routes (`/api/auth/login`, `/api/auth/register`) are public
- All other routes require authentication
- Frontend pages use Axios to communicate with the backend API
- Role-based permissions are enforced in module handlers using the `roles` module
