This is a task management application built with Express.js for the backend and React for the frontend, using MongoDB as the database. Authentication is disabled, so no user login or session management is required.

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

4. Start the MongoDB server:
   Ensure MongoDB is installed and running on your system. You can start it via:
   mongod

   Alternatively, use MongoDB Atlas if preferred.

5. Start the backend server:
   cd backend
   node app.js

   The backend will run on http://localhost:5000

6. Start the frontend development server:
   cd ../frontend
   npm run dev

   The frontend will run on http://localhost:5173

Project Structure

backend/
  app.js              - Express server entry point
  routes/
    index.js          - Aggregates all API routes
  models/
    Task.js           - Mongoose schema for tasks
  .env                - Environment variables (e.g., MONGO_URI)

frontend/
  src/
    pages/
      Dashboard.jsx           - Displays all tasks
      CreateTask.jsx          - Form to create a new task
      TaskDetails.jsx         - View details of a specific task
      CompletedTasks.jsx      - Lists only completed tasks
    App.jsx                   - Main React router configuration
    main.jsx                  - React entry point

API Endpoints

GET     /api/tasks               - Get all tasks
POST    /api/tasks               - Create a new task
GET     /api/tasks/:id           - Get task by ID
PUT     /api/tasks/:id           - Update task by ID
DELETE  /api/tasks/:id           - Delete task by ID
GET     /api/tasks?completed=true - Get only completed tasks

Frontend Pages

- Dashboard: Shows all tasks in a list with options to view details or mark as completed.
- Create Task: Form to add a new task with title, description, and completion status.
- Task Details: Displays full details of a selected task with edit and delete options.
- Completed Tasks: Filters and displays only tasks marked as completed.

Environment Variables

Create a .env file in the backend directory:

MONGO_URI=mongodb://localhost:27017/taskmanager

Ensure the database name (taskmanager) is set appropriately.

Notes

- No authentication is implemented. All endpoints are publicly accessible.
- Tasks are stored in MongoDB using Mongoose.
- The frontend uses React Router to navigate between pages.
- The backend uses Express.js with middleware for JSON parsing and CORS.

Testing

Once both servers are running, visit http://localhost:5173 to interact with the application. Use the browser's developer tools to inspect network requests and ensure API calls are working correctly.

Deployment

For production deployment:

- Use a process manager like PM2 for the backend.
- Build the frontend with npm run build and serve the static files with Express or a CDN.
- Use MongoDB Atlas for a managed database service.
- Set environment variables in your hosting platform.
