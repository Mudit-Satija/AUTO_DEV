ExpenseFlow

A full-stack expense tracking application built with Express.js, React, and MongoDB. Track transactions, manage budgets, and analyze spending patterns across categories.

Features
- Real-time transaction logging with categories
- Monthly budget planning and tracking
- Visual reports and analytics dashboards
- RESTful API backend with MongoDB persistence

Tech Stack
- Backend: Express.js
- Frontend: React (Vite)
- Database: MongoDB (Mongoose ODM)

Setup Instructions

Prerequisites
- Node.js (v18+)
- MongoDB (local or cloud instance)

Backend Setup
1. Navigate to the project root:
   cd expenseflow

2. Install backend dependencies:
   npm install

3. Create a .env file in the root directory:
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/expenseflow

4. Start the Express server:
   npm run dev

Frontend Setup
1. In a new terminal, navigate to the frontend directory:
   cd client

2. Install frontend dependencies:
   npm install

3. Start the React development server:
   npm run dev

4. Open http://localhost:5173 in your browser

API Endpoints
GET /api/transactions - Get all transactions
POST /api/transactions - Create a new transaction
PUT /api/transactions/:id - Update a transaction
DELETE /api/transactions/:id - Delete a transaction

GET /api/budgets - Get all budgets
POST /api/budgets - Create a new budget
PUT /api/budgets/:id - Update a budget
DELETE /api/budgets/:id - Delete a budget

GET /api/categories - Get all categories
POST /api/categories - Create a new category
PUT /api/categories/:id - Update a category
DELETE /api/categories/:id - Delete a category

Frontend Pages
- Dashboard: Overview of current spending and budget status
- Transactions: List and manage all transactions
- Budgets: View and adjust monthly budgets
- Reports: Generate spending reports by category
- Analytics: Interactive charts and trends

Database Models
- Transaction: { amount, description, category, date, type }
- Budget: { category, amount, month, year, isActive }
- Category: { name, color, type }

Note: All data is fetched from the backend API on page load. No data is stored in localStorage.

Running Tests
npm test

Deployment
Build the frontend:
cd client
npm run build

Serve the static files with Express:
npm run build:server

Then deploy the entire project to your preferred platform (Heroku, Render, Vercel, etc.).

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
MIT