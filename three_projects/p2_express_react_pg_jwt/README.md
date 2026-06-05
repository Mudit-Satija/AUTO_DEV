# Project Overview

This is a full-stack application built with Express.js for the backend, React for the frontend, and PostgreSQL as the database. Authentication is handled via JWT, and the system includes modules for users, orders, and products with corresponding frontend pages: Dashboard, Orders, and Products.

## Backend Structure

- **Express.js** serves as the backend framework.
- **PostgreSQL** is used as the relational database.
- **JWT** is used for authentication.
- Required backend modules: `users`, `orders`, `products`.
- All API routes are mounted under `/api`.
- Auth routes (`/auth/login`, `/auth/register`, etc.) are mounted before protected routes.

## Frontend Structure

- **React** with Vite is used for the frontend.
- Authenticated routes are protected via JWT token stored in localStorage.
- Required frontend pages: `Dashboard`, `Orders`, `Products`.
- All API calls are made to `/api` endpoints.

## Database Setup

1. Install PostgreSQL if not already installed.
2. Create a database named `project_db`:
   ```sql
   CREATE DATABASE project_db;
   ```
3. Create the required tables using the SQL scripts in `/backend/db/schema.sql`.

## Setup Instructions

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
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=project_db
   JWT_SECRET=your_jwt_secret_key_here
   ```

4. Run the backend server:
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
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

4. Run the frontend development server:
   ```bash
   npm run dev
   ```

## Authentication Flow

1. User logs in via `/api/auth/login` with email and password.
2. Server responds with a JWT token in the response body.
3. Client stores the token in localStorage.
4. All subsequent requests to protected routes include the token in the `Authorization` header:
   ```
   Authorization: Bearer <token>
   ```
5. Auth middleware verifies the token before allowing access to `/api/users`, `/api/orders`, `/api/products`.

## API Endpoints

### Public Routes (No Auth Required)
- `POST /api/auth/login`
- `POST /api/auth/register`

### Protected Routes (Auth Required)
- `GET /api/users/me`
- `GET /api/users`
- `POST /api/users`
- `PUT /api/users/:id`
- `DELETE /api/users/:id`
- `GET /api/orders`
- `POST /api/orders`
- `PUT /api/orders/:id`
- `DELETE /api/orders/:id`
- `GET /api/products`
- `POST /api/products`
- `PUT /api/products/:id`
- `DELETE /api/products/:id`

## Folder Structure

```
project/
├── backend/
│   ├── app.js
│   ├── routes/
│   │   ├── auth.js
│   │   ├── users.js
│   │   ├── orders.js
│   │   └── products.js
│   ├── controllers/
│   │   ├── authController.js
│   │   ├── userController.js
│   │   ├── orderController.js
│   │   └── productController.js
│   ├── models/
│   │   ├── user.js
│   │   ├── order.js
│   │   └── product.js
│   ├── middleware/
│   │   └── auth.js
│   ├── db/
│   │   └── schema.sql
│   └── .env
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Dashboard.jsx
    │   │   ├── Orders.jsx
    │   │   └── Products.jsx
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── api/
    │       └── index.js
    ├── public/
    └── .env
```

## Dependencies

### Backend
- express
- pg
- jsonwebtoken
- dotenv
- bcrypt

### Frontend
- react
- react-dom
- react-router-dom
- axios

## Running Tests

Testing is not included in this initial setup. Add Jest for backend and Vitest for frontend as needed.

## Deployment

Build the frontend:
```bash
cd frontend
npm run build
```

Serve the static files from `frontend/dist` using Express or a static server like Nginx.

The backend can be deployed using PM2, Docker, or any Node.js hosting provider.

## License

MIT