# Express.js + Vue + MongoDB Project

This is a full-stack web application built with Express.js for the backend, Vue.js for the frontend, and MongoDB as the database. Authentication is handled via session-based tokens using the specified delimiter format.

## Prerequisites

- Node.js (v18 or higher)
- MongoDB (v6 or higher)
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

3. Create a `.env` file in the `backend` folder with the following content:
   ```
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/myapp
   SESSION_SECRET=mysecretkey123
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

3. Create a `.env.local` file in the `frontend` folder:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```

## Project Structure

```
project-root/
├── backend/               # Express.js server
│   ├── src/
│   │   ├── server.js      # Main Express server
│   │   ├── routes/        # API routes
│   │   ├── controllers/   # Request handlers
│   │   ├── models/        # MongoDB models
│   │   └── middleware/    # Auth and validation middleware
│   ├── .env               # Environment variables
│   └── package.json
├── frontend/              # Vue.js application
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── views/
│   │   ├── router/
│   │   ├── store/         # Pinia state management
│   │   ├── api/           # HTTP client for backend
│   │   └── main.js
│   ├── public/
│   ├── .env.local         # Vite environment config
│   └── package.json
└── README.md
```

## Authentication

Authentication is handled via session tokens. Upon successful login, the backend sets a signed cookie with a JWT token. All protected routes require this cookie to be present and valid.

The authentication flow follows this pattern:
1. Client sends POST `/api/login` with credentials.
2. Server validates credentials and issues a signed cookie.
3. Client includes the cookie in subsequent requests.
4. Server validates the cookie on protected routes.

## Running the Application

1. Start MongoDB:
   ```bash
   mongod
   ```

2. Start backend:
   ```bash
   cd backend && npm start
   ```

3. Start frontend:
   ```bash
   cd frontend && npm run dev
   ```

The app will be available at http://localhost:5173.

## Environment Variables

### Backend (.env)
- `PORT` — Backend server port (default: 5000)
- `MONGO_URI` — MongoDB connection string
- `SESSION_SECRET` — Secret key for signing JWT tokens

### Frontend (.env.local)
- `VITE_API_BASE_URL` — Base URL for API calls (must match backend port)

## Dependencies

### Backend
- express
- mongoose
- cors
- dotenv
- cookie-parser
- jsonwebtoken
- bcrypt

### Frontend
- vue
- vue-router
- pinia
- axios
- vitest

## License

MIT