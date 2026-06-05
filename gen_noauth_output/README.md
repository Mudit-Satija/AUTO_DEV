# Project Overview

This is a full-stack application built with Express.js for the backend and React for the frontend, using MongoDB as the database. Authentication is disabled, so no user login, tokens, or session management is implemented.

The backend exposes two modules: `posts` and `inventory`.  
The frontend provides two pages: `Dashboard` and `Posts`.

## Project Structure

### Backend (Express.js)
- `src/`
  - `app.js` — Main Express application entry point
  - `routes/`
    - `posts.js` — Routes for posts module
    - `inventory.js` — Routes for inventory module
    - `index.js` — Aggregates all API routes under `/api`
  - `models/`
    - `Post.js` — Mongoose schema for posts
    - `Inventory.js` — Mongoose schema for inventory
  - `services/`
    - `postService.js` — Business logic for posts
    - `inventoryService.js` — Business logic for inventory

### Frontend (React + Vite)
- `src/`
  - `pages/`
    - `Dashboard.jsx` — Dashboard page component
    - `Posts.jsx` — Posts page component
  - `App.jsx` — Main React router component
  - `main.jsx` — Entry point for React

## Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- MongoDB (local or cloud instance)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install backend dependencies:
   ```bash
   cd src
   npm install express mongoose cors dotenv
   ```

3. Create a `.env` file in `src/`:
   ```
   MONGO_URI=mongodb://localhost:27017/projectdb
   PORT=5000
   ```

4. Start the backend server:
   ```bash
   node app.js
   ```

### Frontend Setup

1. Install frontend dependencies:
   ```bash
   cd ../
   npm install react react-dom react-router-dom axios
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

### Database

The application uses MongoDB via Mongoose. Ensure MongoDB is running locally or update `MONGO_URI` in `.env` to point to your MongoDB instance.

The following collections will be automatically created on first use:
- `posts`
- `inventory`

## API Endpoints

All endpoints are prefixed with `/api`.

### Posts Module
- `GET /api/posts` — Get all posts
- `POST /api/posts` — Create a new post
- `GET /api/posts/:id` — Get a specific post
- `PUT /api/posts/:id` — Update a post
- `DELETE /api/posts/:id` — Delete a post

### Inventory Module
- `GET /api/inventory` — Get all inventory items
- `POST /api/inventory` — Add a new inventory item
- `GET /api/inventory/:id` — Get a specific inventory item
- `PUT /api/inventory/:id` — Update an inventory item
- `DELETE /api/inventory/:id` — Delete an inventory item

## Frontend Pages

- **Dashboard**: Displays an overview of posts and inventory counts.
- **Posts**: Lists all posts with options to create, edit, or delete.

## Notes

- No authentication is implemented. All endpoints are publicly accessible.
- All data is stored in MongoDB. No SQL databases are used.
- Frontend components use Axios to communicate with the Express backend.
- Environment variables are used for configuration (e.g., MongoDB URI, port).