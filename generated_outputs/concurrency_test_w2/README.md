ExpenseFlow

A full-stack expense tracking application built with Express.js, React, and MongoDB. Track transactions, manage budgets, and visualize spending with intuitive dashboards and analytics.

Features
- Real-time transaction logging with categories
- Monthly budget planning and tracking
- Interactive reports and spending analytics
- Responsive dashboard with summary metrics

Tech Stack
- Backend: Express.js
- Frontend: React (Vite)
- Database: MongoDB (Mongoose)
- SRS Entities: Transaction, Budget, Category
- SRS Pages: Dashboard, Transactions, Budgets, Reports, Analytics

Setup Instructions

Prerequisites
- Node.js (v18+)
- MongoDB (local or cloud instance)

Backend Setup
1. Navigate to the project root
2. Install backend dependencies:
   npm install

3. Create a .env file in the root directory:
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/expenseflow

4. Start the Express server:
   npm run dev

Frontend Setup
1. Navigate to the client directory:
   cd client

2. Install frontend dependencies:
   npm install

3. Start the React development server:
   npm run dev

4. Open http://localhost:5173 in your browser

Database Schema
- Transaction: { amount, category, description, date, type }
- Budget: { category, amount, month, year, spent }
- Category: { name, type, color }

API Endpoints
GET /api/transactions          - Get all transactions
POST /api/transactions         - Create a new transaction
PUT /api/transactions/:id      - Update a transaction
DELETE /api/transactions/:id   - Delete a transaction

GET /api/budgets               - Get all budgets
POST /api/budgets              - Create a new budget
PUT /api/budgets/:id           - Update a budget
DELETE /api/budgets/:id        - Delete a budget

GET /api/categories            - Get all categories

Frontend Pages
- Dashboard: Summary of spending, budget progress, and recent transactions
- Transactions: List and manage all transactions
- Budgets: View and edit monthly budgets by category
- Reports: Generate visual reports of spending patterns
- Analytics: Interactive charts and trend analysis

Project Structure
.
├── server/
│   ├── config/
│   │   └── db.js
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
│   └── server.js
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
    ├── public/
    └── vite.config.js

Running Tests
npm test  # Backend unit tests (if implemented)
npm test  # Frontend unit tests (if implemented)

Deployment
Build the frontend:
cd client
npm run build

Serve the static files with Express:
node server/app.js

Environment variables are loaded automatically from .env in both server and client directories.

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
MIT