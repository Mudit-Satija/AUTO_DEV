ExpenseFlow

A full-stack expense tracking application built with Express.js, React, and MongoDB. Track transactions, manage budgets, and analyze spending patterns across categories.

Features
- Real-time transaction logging with categories
- Monthly budget planning and tracking
- Interactive reports and analytics dashboards
- RESTful API backend with MongoDB persistence
- Responsive React frontend with routing

Tech Stack
- Backend: Express.js
- Frontend: React (Vite)
- Database: MongoDB (via Mongoose)
- SRS Entities: Transaction, Budget, Category
- SRS Pages: Dashboard, Transactions, Budgets, Reports, Analytics

Setup Instructions

Backend Setup
1. Navigate to the project root directory
2. Install dependencies:
   npm install

3. Create a .env file in the root directory:
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/expenseflow

4. Start the backend server:
   npm run dev

Frontend Setup
1. Navigate to the client directory:
   cd client

2. Install dependencies:
   npm install

3. Start the frontend development server:
   npm run dev

4. Open http://localhost:5173 in your browser

Database
MongoDB is required. Ensure MongoDB is running locally on port 27017, or update MONGO_URI in .env to point to your MongoDB instance.

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
- Reports: Generate spending reports by category and time period
- Analytics: Visualize trends and spending patterns

Project Structure
/
├── server/
│   ├── models/
│   │   ├── Transaction.js
│   │   ├── Budget.js
│   │   └── Category.js
│   ├── routes/
│   │   ├── transactions.js
│   │   ├── budgets.js
│   │   ├── categories.js
│   │   └── index.js
│   ├── app.js
│   └── config/
│       └── db.js
└── client/
    ├── src/
    │   ├── pages/
    │   │   ├── Dashboard.jsx
    │   │   ├── Transactions.jsx
    │   │   ├── Budgets.jsx
    │   │   ├── Reports.jsx
    │   │   └── Analytics.jsx
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── index.html
    └── vite.config.js

Running the Full Application
1. Start MongoDB (if not already running)
2. Start backend server: npm run dev (from root)
3. Start frontend server: npm run dev (from client/)

The frontend will automatically connect to http://localhost:5000/api for all API requests.

Note: Ensure all dependencies are installed in both root and client directories. Use separate terminal tabs for backend and frontend servers during development.