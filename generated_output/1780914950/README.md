Project Overview

This is a full-stack application built with Express.js for the backend and React for the frontend, using MongoDB as the database. Authentication is disabled, so no user login, sessions, or tokens are required.

The backend exposes two modules: tasks and categories. The frontend provides three pages: Dashboard, Tasks, and Categories.

Setup Instructions

1. Clone the repository:
   git clone <repository-url>
   cd <project-directory>

2. Install backend dependencies:
   cd backend
   npm install

3. Install frontend dependencies:
   cd ../frontend
   npm install

4. Start the MongoDB service:
   Ensure MongoDB is running on your system. If using MongoDB Compass or Atlas, ensure the connection string is set in backend/.env.

5. Set environment variables (backend/.env):
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/project-db

6. Start the backend server:
   cd backend
   node app.js

7. Start the frontend development server:
   cd frontend
   npm run dev

8. Open your browser and navigate to:
   http://localhost:5173

The frontend will automatically connect to the backend at http://localhost:5000/api.

Project Structure

backend/
├── app.js             # Express server entry point
├── .env               # Environment variables
├── routes/
│   ├── tasks.js       # Routes for tasks module
│   └── categories.js  # Routes for categories module
├── models/
│   ├── Task.js        # Mongoose schema for tasks
│   └── Category.js    # Mongoose schema for categories
└── utils/
    └── connectDB.js   # MongoDB connection utility

frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx  # Dashboard page component
│   │   ├── Tasks.jsx      # Tasks page component
│   │   └── Categories.jsx # Categories page component
│   ├── App.jsx            # Main React router component
│   └── main.jsx           # React entry point
└── vite.config.js         # Vite configuration

Note: No authentication middleware or user models are included, as auth is disabled per project rules.

Database Schema

Task model:
- title: String (required)
- description: String
- categoryId: ObjectId (reference to Category)
- createdAt: Date
- updatedAt: Date

Category model:
- name: String (required)
- description: String
- createdAt: Date
- updatedAt: Date

API Endpoints

GET /api/tasks           - Get all tasks
POST /api/tasks          - Create a new task
GET /api/tasks/:id       - Get a task by ID
PUT /api/tasks/:id       - Update a task
DELETE /api/tasks/:id    - Delete a task

GET /api/categories      - Get all categories
POST /api/categories     - Create a new category
GET /api/categories/:id  - Get a category by ID
PUT /api/categories/:id  - Update a category
DELETE /api/categories/:id - Delete a category

Frontend Pages

- Dashboard: Shows an overview of tasks and categories.
- Tasks: Lists all tasks with create, read, update, and delete actions.
- Categories: Lists all categories with create, read, update, and delete actions.

All API calls are made to http://localhost:5000/api without authentication headers.

Troubleshooting

- If you get a connection error to MongoDB, ensure mongod is running and MONGO_URI is correct.
- If the frontend fails to load, ensure the backend is running and accessible at http://localhost:5000.
- If CORS errors occur, ensure the backend is configured to allow requests from http://localhost:5173 (Vite default).