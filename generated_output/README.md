Project Overview

This is a full-stack application built with Express.js for the backend and React for the frontend, using MongoDB as the database. Authentication is disabled, so no user login, tokens, or session management is implemented.

The backend exposes two modules: tasks and categories. The frontend provides three pages: Dashboard, Tasks, and Categories.

Setup Instructions

1. Prerequisites
   - Node.js (v18 or higher)
   - MongoDB (running locally or accessible via environment variable MONGO_URI)

2. Backend Setup
   - Navigate to the project root directory.
   - Install backend dependencies:
     npm install express mongoose cors dotenv

   - Create a .env file in the root directory:
     MONGO_URI=mongodb://localhost:27017/projectdb

   - Start the backend server:
     node app.js

3. Frontend Setup
   - Navigate to the frontend directory:
     cd client

   - Install frontend dependencies:
     npm install

   - Start the React development server:
     npm run dev

4. Access the Application
   - Backend API: http://localhost:5000/api
   - Frontend UI: http://localhost:5173

File Structure

Backend:
- app.js            - Express server entry point
- routes/
  - tasks.js        - Task-related routes
  - categories.js   - Category-related routes
- models/
  - Task.js         - Mongoose schema for tasks
  - Category.js     - Mongoose schema for categories
- config/
  - db.js           - MongoDB connection setup

Frontend:
- src/
  - pages/
    - Dashboard.jsx - Dashboard page component
    - Tasks.jsx     - Tasks page component
    - Categories.jsx - Categories page component
  - App.jsx         - Main React router
  - main.jsx        - React entry point

Notes
- No authentication middleware is used or required.
- All routes are publicly accessible.
- MongoDB is used exclusively; no SQL databases are involved.
- React uses Vite for development and bundling.
