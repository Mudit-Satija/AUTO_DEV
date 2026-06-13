ExpenseFlow

A full-stack expense tracking application built with Express.js, React, and MongoDB. Track transactions, manage budgets, and analyze spending patterns across categories.

Features
- Real-time transaction logging with categories
- Monthly budget planning and tracking
- Interactive reports and analytics dashboards
- Responsive UI with navigation between all modules

Backend
- Built with Express.js
- MongoDB for data persistence using Mongoose
- RESTful API endpoints for Transaction, Budget, and Category entities
- Connected via Mongoose to MongoDB Atlas or local instance

Frontend
- Built with React and Vite
- Pages: Dashboard, Transactions, Budgets, Reports, Analytics
- Client-side routing with React Router
- All data fetched from backend API on mount — no localStorage used

Prerequisites
- Node.js (v18+)
- MongoDB (v6+)
- npm or yarn

Setup Instructions

1. Clone the repository
git clone https://github.com/yourusername/expenseflow.git
cd expenseflow

2. Install backend dependencies
cd backend
npm install

3. Install frontend dependencies
cd ../frontend
npm install

4. Configure MongoDB connection
Create a .env file in the backend directory:

MONGO_URI=mongodb://localhost:27017/expenseflow
PORT=5000

Replace mongodb://localhost:27017/expenseflow with your MongoDB connection string (e.g., MongoDB Atlas URI).

5. Start the backend server
cd backend
npm run dev

6. Start the frontend development server
cd ../frontend
npm run dev

7. Open your browser to http://localhost:5173

Directory Structure

backend/
├── models/
│   ├── Transaction.js
│   ├── Budget.js
│   └── Category.js
├── routes/
│   ├── index.js
│   ├── transactions.js
│   ├── budgets.js
│   └── categories.js
├── config/
│   └── db.js
├── app.js
└── server.js

frontend/
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
└── vite.config.js

API Endpoints

GET /api/transactions — Get all transactions
POST /api/transactions — Create a new transaction
PUT /api/transactions/:id — Update a transaction
DELETE /api/transactions/:id — Delete a transaction

GET /api/budgets — Get all budgets
POST /api/budgets — Create a new budget
PUT /api/budgets/:id — Update a budget
DELETE /api/budgets/:id — Delete a budget

GET /api/categories — Get all categories
POST /api/categories — Create a new category
PUT /api/categories/:id — Update a category
DELETE /api/categories/:id — Delete a category

Deployment
Build the frontend:
cd frontend
npm run build

Serve the static files with Express or any static server (e.g., nginx, Vercel, Netlify).

The backend can be deployed to any Node.js hosting provider (Render, Railway, Heroku, etc.).

License
MIT