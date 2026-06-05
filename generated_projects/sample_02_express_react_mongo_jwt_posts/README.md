# Express.js + React + MongoDB + JWT Project

This is a full-stack web application built with Express.js for the backend, React for the frontend, MongoDB as the database, and JWT for authentication.

## Features

- RESTful API endpoints using Express.js
- JWT-based user authentication and authorization
- React frontend with state management and routing
- MongoDB for data persistence
- Environment variable configuration
- CORS enabled for frontend-backend communication

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- MongoDB (local or cloud instance)

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

3. Create a `.env` file in the `backend` directory:
   ```
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/your-db-name
   JWT_SECRET=your-super-secret-jwt-key-here
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

3. Create a `.env` file in the `frontend` directory:
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   ```

4. Start the frontend development server:
   ```bash
   npm start
   ```

## Project Structure

```
project-root/
├── backend/                  # Express.js server
│   ├── controllers/          # Route controllers
│   ├── models/               # MongoDB models
│   ├── routes/               # API routes
│   ├── middleware/           # Auth and custom middleware
│   ├── .env                  # Environment variables
│   ├── server.js             # Main server entry point
│   └── package.json
├── frontend/                 # React application
│   ├── public/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components
│   │   ├── context/          # Auth and state context
│   │   ├── services/         # API service calls
│   │   ├── App.js
│   │   └── index.js
│   ├── .env                  # Environment variables
│   └── package.json
└── README.md
```

## Authentication Flow

1. User logs in via `/api/auth/login` with email and password.
2. Server validates credentials and issues a signed JWT.
3. JWT is stored in localStorage on the frontend.
4. Subsequent requests include the JWT in the Authorization header: `Bearer <token>`.
5. Middleware verifies the token on protected routes.
6. On logout, the token is removed from localStorage.

## Environment Variables

### Backend (.env)
- `PORT`: Server port (default: 5000)
- `MONGO_URI`: MongoDB connection string
- `JWT_SECRET`: Secret key for signing JWTs (use a strong random string)

### Frontend (.env)
- `REACT_APP_API_URL`: Base URL of the backend API

## Running in Production

1. Build the React app:
   ```bash
   cd frontend
   npm run build
   ```

2. Serve the React build from Express:
   - In `backend/server.js`, ensure static file serving is enabled for the `frontend/build` directory.
   - Use a process manager like PM2 to run the backend in production.

## License

MIT