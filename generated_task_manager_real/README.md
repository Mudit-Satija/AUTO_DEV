# Calculator Project

A simple calculator application built with Express.js backend and React frontend, using MongoDB as the database. Authentication is disabled.

## Features

- Backend: Express.js with MongoDB/Mongoose
- Frontend: React with Vite
- Calculator functionality exposed via API
- No authentication required

## Prerequisites

- Node.js (v18 or higher)
- MongoDB (local or cloud instance)
- npm or yarn

## Setup

### Backend Setup

1. Navigate to the project root directory:

```bash
cd backend
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file in the `backend` directory:

```env
MONGO_URI=mongodb://localhost:27017/calculator-db
PORT=5000
```

4. Start the backend server:

```bash
npm start
```

The backend will run on `http://localhost:5000`.

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will run on `http://localhost:5173`.

## API Endpoints

The backend exposes the following API routes under `/api`:

- `POST /api/calculate` — Performs a calculation with provided operands and operator

Request body example:

```json
{
  "operand1": 10,
  "operand2": 5,
  "operator": "+"
}
```

Response example:

```json
{
  "result": 15
}
```

## Project Structure

### Backend

- `app.js` — Express app configuration and route mounting
- `routes/calculator.js` — Calculator API routes
- `controllers/calculator.js` — Calculator logic controller
- `models/calculator.js` — Mongoose model for storing calculation history
- `config/db.js` — MongoDB connection setup
- `.env` — Environment variables

### Frontend

- `src/pages/Calculator.jsx` — Main calculator UI component
- `src/main.jsx` — React entry point
- `vite.config.js` — Vite configuration

## Database

The application uses MongoDB to store calculation history. The `calculator` model stores:

- `operand1`: Number
- `operand2`: Number
- `operator`: String (+, -, *, /)
- `result`: Number
- `timestamp`: Date

## Testing

To test the API manually:

```bash
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"operand1": 7, "operand2": 3, "operator": "*"}'
```

Expected response:

```json
{"result":21}
```

## License

MIT