Project Overview

This is a task management application built with Express.js for the backend and React for the frontend, using MongoDB as the database. Authentication is disabled, so no user login or session management is required.

The application provides two frontend pages:
- PendingTasks: Displays tasks that are not yet completed.
- CompletedTasks: Displays tasks that have been marked as completed.

Backend Setup

1. Install dependencies:
   npm install express mongoose cors dotenv

2. Create a .env file in the root directory and set your MongoDB connection string:
   MONGO_URI=mongodb://localhost:27017/taskmanager

3. Start the backend server:
   node app.js

Frontend Setup

1. Navigate to the frontend directory:
   cd frontend

2. Install dependencies:
   npm install

3. Start the development server:
   npm run dev

Database

The application uses MongoDB with Mongoose. No collections are pre-defined — they are created automatically when tasks are first saved. The Task model includes fields for title, description, status (pending/completed), and timestamps.

Usage

- The backend API is accessible at http://localhost:5000/api
- The frontend is served at http://localhost:5173
- Navigate to the frontend to view and manage tasks
- No authentication is required

Note: This project does not include any authentication middleware, user models, or token handling. All routes are publicly accessible.
