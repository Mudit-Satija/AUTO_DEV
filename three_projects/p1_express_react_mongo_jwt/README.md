# Project Overview

This is a full-stack application built with Express.js for the backend, React for the frontend, and MongoDB as the database. Authentication is handled via JWT. The system includes three backend modules: posts, inventory, and roles. The frontend features three pages: Dashboard, Posts, and Inventory.

## Features

- JWT-based authentication
- Protected routes for authenticated users
- Modular backend structure with posts, inventory, and roles
- React frontend with Dashboard, Posts, and Inventory pages
- MongoDB for data persistence using Mongoose

## Setup Instructions

### Prerequisites

- Node.js (v18 or higher)
- MongoDB (local or cloud instance)
- npm or yarn

### Backend Setup

1. Navigate to the project root directory:

   ```bash
   cd backend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Create a `.env` file in the `backend` directory with the following variables:

   ```
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/your-db-name
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

3. Create a `.env` file in the `frontend` directory with the backend URL:

   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

4. Start the frontend development server:

   ```bash
   npm run dev
   ```

### Authentication Flow

- Users can log in via the `/api/auth/login` endpoint.
- Upon successful login, a JWT token is returned.
- The token must be included in the `Authorization` header for protected routes as: `Bearer <token>`.
- Protected routes include `/api/posts`, `/api/inventory`, and `/api/roles`.

### Directory Structure

#### Backend

```
backend/
├── app.js
├── routes/
│   ├── auth.js
│   └── index.js
├── controllers/
│   ├── posts.js
│   ├── inventory.js
│   └── roles.js
├── models/
│   ├── Post.js
│   ├── Inventory.js
│   └── Role.js
├── middleware/
│   └── auth.js
├── services/
│   ├── posts.js
│   ├── inventory.js
│   └── roles.js
└── .env
```

#### Frontend

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
│       └── client.js
├── index.html
└── vite.config.js
```

### Running the Application

1. Ensure MongoDB is running.
2. Start the backend server.
3. Start the frontend server.
4. Open http://localhost:5173 in your browser.

The application will redirect unauthenticated users to a login page (not implemented in this scope but expected to be added in future iterations). Authenticated users can navigate to Dashboard, Posts, and Inventory pages.

### Testing

Use tools like Postman or curl to test API endpoints:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

Use the returned token in subsequent requests:

```bash
curl -X GET http://localhost:5000/api/posts \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Environment Variables

Ensure all required environment variables are set in `.env` files for both backend and frontend.

### Deployment

- Backend: Deploy to any Node.js-compatible platform (e.g., Render, Railway, Heroku).
- Frontend: Deploy to any static host (e.g., Vercel, Netlify, GitHub Pages).
- MongoDB: Use MongoDB Atlas for cloud deployment.

For production, rotate JWT_SECRET and enable HTTPS.