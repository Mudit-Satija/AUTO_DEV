ExpenseFlow

A full-stack expense tracking application built with Express.js, React, and MongoDB. Track transactions, manage budgets, and analyze spending patterns across categories.

Features
- Real-time transaction logging with categories
- Monthly budget planning and tracking
- Interactive dashboards and financial reports
- Data-driven analytics visualizations

Backend (Express.js)
- RESTful API endpoints for Transaction, Budget, and Category entities
- MongoDB with Mongoose for data persistence
- Routes mounted under /api
- Connects to MongoDB on startup

Frontend (React)
- Single Page Application with React Router
- Pages: Dashboard, Transactions, Budgets, Reports, Analytics
- All data fetched from backend API on mount (no localStorage)
- Responsive navigation header for seamless page switching

Setup Instructions

Prerequisites
- Node.js (v18+)
- MongoDB (local or cloud instance)

Backend Setup
1. Navigate to the project root
2. Install backend dependencies:
   npm install express mongoose cors dotenv

3. Create a .env file in the root directory:
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/expenseflow

4. Start the backend server:
   node server.js

Frontend Setup
1. Navigate to the frontend directory (usually ./client)
2. Install frontend dependencies:
   npm install react react-dom react-router-dom

3. Start the development server:
   npm run dev

Database Schema
- Transaction: { amount, description, category, date, type }
- Budget: { category, amount, month, year }
- Category: { name, type }

API Endpoints
GET /api/transactions - Get all transactions
POST /api/transactions - Create a new transaction
GET /api/transactions/:id - Get transaction by ID
PUT /api/transactions/:id - Update transaction
DELETE /api/transactions/:id - Delete transaction

GET /api/budgets - Get all budgets
POST /api/budgets - Create a new budget
GET /api/budgets/:id - Get budget by ID
PUT /api/budgets/:id - Update budget
DELETE /api/budgets/:id - Delete budget

GET /api/categories - Get all categories
POST /api/categories - Create a new category
GET /api/categories/:id - Get category by ID
PUT /api/categories/:id - Update category
DELETE /api/categories/:id - Delete category

Frontend Pages
- Dashboard: Summary of recent transactions and budget status
- Transactions: List and manage all transactions
- Budgets: View and edit monthly budgets by category
- Reports: Generate spending reports by category and time period
- Analytics: Visual charts and trends for spending behavior

Usage
1. Start the backend server
2. Start the frontend development server
3. Open http://localhost:5173 in your browser
4. Navigate between pages using the header navigation

Note: All pages fetch live data from the backend on mount. No data is stored in localStorage.
