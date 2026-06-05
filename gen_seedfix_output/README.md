# Project Overview

This is a full-stack application built with Express.js for the backend and React for the frontend, using MongoDB as the database. Authentication is disabled, so no user login, tokens, or session management is implemented.

The backend provides two modules: `posts` and `inventory`.  
The frontend includes two pages: `Dashboard` and `Posts`.

## Project Structure

### Backend (Express.js)
- `app.js` — Main Express application entry point
- `routes/` — Contains route handlers for `posts` and `inventory`
- `models/` — Mongoose schemas for `posts` and `inventory`
- `services/` — Business logic for data operations

### Frontend (React)
- `src/pages/Dashboard.jsx` — Dashboard view
- `src/pages/Posts.jsx` — Posts view
- `src/App.jsx` — Main React router configuration
- `src/main.jsx` — Entry point for React app

## Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- MongoDB (local or cloud instance)
- npm or yarn

### Backend Setup

1. Navigate to the project root:
   ```bash
   cd project-root
   ```

2. Install backend dependencies:
   ```bash
   npm install express mongoose cors dotenv
   ```

3. Create a `.env` file in the root directory:
   ```
   PORT=5000
   MONGODB_URI=mongodb://127.0.0.1:27017/project-db
   ```

4. Start the backend server:
   ```bash
   node app.js
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install react react-dom react-router-dom
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Database Setup

Ensure MongoDB is running. The application connects to `mongodb://127.0.0.1:27017/project-db` by default.  
You can change the database URI in the `.env` file.

### Accessing the Application

- Backend API: `http://localhost:5000/api/posts` and `http://localhost:5000/api/inventory`
- Frontend UI: `http://localhost:5173`

No authentication is required. All endpoints and pages are publicly accessible.
