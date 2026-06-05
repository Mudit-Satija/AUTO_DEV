# Project Overview

This is a full-stack application built with FastAPI as the backend and React as the frontend, using MongoDB as the database. Authentication is disabled, so no user login, tokens, or session management is implemented.

The backend exposes two modules: tasks and notes.  
The frontend includes three pages: Dashboard, Tasks, and Notes.

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB installed and running locally (or accessible via environment variable MONGO_URI)

## Backend Setup

1. Navigate to the backend directory:

   cd backend

2. Install dependencies:

   pip install fastapi uvicorn motor python-dotenv

3. Start the FastAPI server:

   uvicorn app.main:app --reload

   The API will be available at http://localhost:8000

## Frontend Setup

1. Navigate to the frontend directory:

   cd frontend

2. Install dependencies:

   npm install

3. Start the React development server:

   npm run dev

   The frontend will be available at http://localhost:5173

## Directory Structure

### Backend (app/)

- main.py: FastAPI app entry point
- tasks/ : Routes and logic for task management
- notes/ : Routes and logic for note management

### Frontend (src/)

- pages/Dashboard.jsx: Dashboard page component
- pages/Tasks.jsx: Tasks management page component
- pages/Notes.jsx: Notes management page component

## API Endpoints

The backend automatically exposes the following endpoints:

- GET /tasks/ - List all tasks
- POST /tasks/ - Create a new task
- GET /tasks/{id} - Get a specific task
- PUT /tasks/{id} - Update a task
- DELETE /tasks/{id} - Delete a task

- GET /notes/ - List all notes
- POST /notes/ - Create a new note
- GET /notes/{id} - Get a specific note
- PUT /notes/{id} - Update a note
- DELETE /notes/{id} - Delete a note

All endpoints are accessible without authentication.

## Database

MongoDB is used as the database. Collections are automatically created on first write:

- tasks: Stores task documents with fields: title, description, createdAt, updatedAt
- notes: Stores note documents with fields: title, content, createdAt, updatedAt

No schema validation is enforced beyond basic field types.

## Notes

- No authentication is implemented.
- All data is publicly accessible.
- CORS is enabled for localhost:5173 by default.
- Environment variables are loaded from .env if present.
