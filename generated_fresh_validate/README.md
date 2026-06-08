# Task Management System

A full-stack task management application built with Express.js, React, and MongoDB, featuring JWT-based authentication.

## Features

- User registration and login with JWT authentication
- Manage tasks with categories
- Protected routes for authenticated users only
- Clean separation of concerns with modular backend structure
- Responsive React frontend with dedicated pages for each feature

## Backend Structure

- **tasks**: Handles task creation, reading, updating, and deletion
- **categories**: Manages task categories
- **users**: Handles user registration, login, and authentication
- **app.js**: Main Express server with MongoDB connection and route mounting

## Frontend Structure

- **Dashboard**: Overview of tasks and categories
- **Tasks**: List and manage tasks
- **Categories**: List and manage categories
- **Login**: User authentication form
- **Register**: User registration form

## Prerequisites

- Node.js (v18+)
- MongoDB (local or cloud instance)
- npm or yarn

## Setup Instructions

### Backend Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install backend dependencies:
   ```
   cd backend
   npm install
   ```

3. Create a `.env` file in the `backend` directory:
   ```
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/taskmanager
   JWT_SECRET=your_jwt_secret_key_here
   ```

4. Start the backend server:
   ```
   npm start
   ```

### Frontend Setup

1. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

2. Create a `.env` file in the `frontend` directory:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

3. Start the frontend development server:
   ```
   npm run dev
   ```

## Database

The application uses MongoDB with Mongoose ODM. Collections created automatically:
- `users`
- `categories`
- `tasks`

## Authentication

JWT authentication is enabled. Upon successful login, a JWT token is returned and stored in localStorage. This token is sent in the Authorization header for protected routes.

## API Endpoints

### Auth Routes (Public)
- POST /api/auth/register
- POST /api/auth/login

### Protected Routes (Require JWT)
- GET /api/tasks
- POST /api/tasks
- PUT /api/tasks/:id
- DELETE /api/tasks/:id
- GET /api/categories
- POST /api/categories
- PUT /api/categories/:id
- DELETE /api/categories/:id
- GET /api/users/me

## Folder Structure

```
project/
├── backend/
│   ├── app.js
│   ├── routes/
│   │   ├── tasks.js
│   │   ├── categories.js
│   │   ├── users.js
│   │   └── index.js
│   ├── controllers/
│   │   ├── tasksController.js
│   │   ├── categoriesController.js
│   │   └── usersController.js
│   ├── models/
│   │   ├── Task.js
│   │   ├── Category.js
│   │   └── User.js
│   ├── middleware/
│   │   └── auth.js
│   └── .env
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Dashboard.jsx
    │   │   ├── Tasks.jsx
    │   │   ├── Categories.jsx
    │   │   ├── Login.jsx
    │   │   └── Register.jsx
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── .env
    └── package.json
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)