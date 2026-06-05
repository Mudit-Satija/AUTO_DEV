# Express.js + React + PostgreSQL + JWT Project

A full-stack web application built with Express.js for the backend, React for the frontend, PostgreSQL as the database, and JWT for authentication.

## Technologies Used

- **Backend**: Express.js (Node.js)
- **Frontend**: React (with React Router, Axios, Context API)
- **Database**: PostgreSQL
- **Authentication**: JSON Web Tokens (JWT)
- **Environment Variables**: dotenv
- **ORM**: pg (native PostgreSQL client) or Sequelize (optional)
- **Build Tool**: Webpack / Vite (React)
- **Testing**: Jest / Supertest (backend), React Testing Library (frontend)

## Project Structure

```
project-root/
├── backend/                 # Express.js server
│   ├── controllers/         # Route controllers
│   ├── models/              # Database models
│   ├── routes/              # API routes
│   ├── middleware/          # Auth and validation middleware
│   ├── config/              # Database and JWT config
│   ├── utils/               # Helper functions
│   ├── .env                 # Environment variables
│   ├── server.js            # Main server entry point
│   └── package.json
├── frontend/                # React application
│   ├── public/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page-level components
│   │   ├── context/         # Auth and state context
│   │   ├── services/        # API calls (Axios)
│   │   ├── App.js
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env                 # Frontend environment variables
│   ├── package.json
│   └── vite.config.js       # or webpack.config.js
├── database/                # SQL schema and seed files
│   ├── schema.sql
│   └── seeds.sql
├── README.md
└── .gitignore
```

## Setup Instructions

### Prerequisites

- Node.js (v18+)
- npm or yarn
- PostgreSQL (v14+)
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the `backend/` directory:
   ```
   PORT=5000
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   JWT_SECRET=your_jwt_secret_key_here
   JWT_EXPIRES_IN=7d
   ```

4. Start PostgreSQL server and create the database:
   ```bash
   createdb your_db_name
   ```

5. Run the schema and seed files (if provided):
   ```bash
   psql -U your_db_user -d your_db_name -f ../database/schema.sql
   psql -U your_db_user -d your_db_name -f ../database/seeds.sql
   ```

6. Start the backend server:
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

3. Create a `.env` file in the `frontend/` directory:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```

## API Endpoints (Backend)

- `POST /api/auth/register` — Register a new user
- `POST /api/auth/login` — Login and receive JWT token
- `GET /api/auth/me` — Get current user (protected)
- `PUT /api/auth/me` — Update current user (protected)
- `POST /api/logout` — Logout (invalidate token on client)

All protected routes require a valid JWT token in the `Authorization` header:
```
Authorization: Bearer <token>
```

## Authentication Flow

1. User registers or logs in via frontend form.
2. Backend validates credentials and returns a JWT token on success.
3. Frontend stores the token in localStorage or sessionStorage.
4. On subsequent requests, the token is sent in the `Authorization` header.
5. Backend middleware verifies the token’s signature and expiration.
6. If valid, the request proceeds; otherwise, a 401 error is returned.

## Database Schema (Example)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Security Best Practices

- Passwords are hashed using bcrypt.
- JWT secrets are stored in environment variables.
- HTTPS is enforced in production.
- Input validation and sanitization are applied on all endpoints.
- CORS is configured to allow only trusted origins in production.
- Tokens are set with short expiration times and refreshed via refresh tokens if needed.

## Deployment

### Backend (Production)

- Use PM2 or systemd to run the Node.js server.
- Place behind a reverse proxy like Nginx.
- Use environment variables for production secrets.
- Enable SSL/TLS via Let’s Encrypt or a cloud provider.

### Frontend (Production)

- Build the React app:
  ```bash
  npm run build
  ```
- Serve static files using Nginx, Vercel, Netlify, or AWS S3.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)