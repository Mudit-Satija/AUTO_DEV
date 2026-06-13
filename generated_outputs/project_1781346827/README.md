ExpenseFlow

A full-stack expense tracking application built with Express.js, React, and MongoDB. Track transactions, manage budgets, and analyze spending with intuitive dashboards and reports.

Features
- Real-time transaction logging with categories
- Monthly budget planning and tracking
- Visual analytics and spending reports
- Responsive dashboard with summary metrics
- RESTful API backend with MongoDB persistence

Tech Stack
- Backend: Express.js
- Frontend: React (Vite)
- Database: MongoDB (Mongoose ODM)
- SRS Entities: Transaction, Budget, Category
- SRS Pages: Dashboard, Transactions, Budgets, Reports, Analytics

Setup Instructions

Prerequisites
- Node.js (v18+)
- MongoDB (local or cloud instance)

Backend Setup
1. Navigate to the project root:
   cd expenseflow

2. Install backend dependencies:
   cd backend
   npm install

3. Create a .env file in backend/ with:
   MONGO_URI=mongodb://localhost:27017/expenseflow
   PORT=5000

4. Start the Express server:
   npm run dev

Frontend Setup
1. In a new terminal, navigate to the frontend directory:
   cd frontend

2. Install frontend dependencies:
   npm install

3. Start the React dev server:
   npm run dev

The app will be available at http://localhost:5173

Database Schema
- Transaction: { amount: Number, description: String, category: ObjectId, date: Date, type: String }
- Budget: { category: ObjectId, amount: Number, month: String, year: Number }
- Category: { name: String, color: String, type: String }

API Endpoints
GET /api/transactions        - Get all transactions
POST /api/transactions       - Create a transaction
PUT /api/transactions/:id    - Update a transaction
DELETE /api/transactions/:id - Delete a transaction

GET /api/budgets             - Get all budgets
POST /api/budgets            - Create a budget
PUT /api/budgets/:id         - Update a budget
DELETE /api/budgets/:id      - Delete a budget

GET /api/categories          - Get all categories
POST /api/categories         - Create a category
PUT /api/categories/:id      - Update a category
DELETE /api/categories/:id   - Delete a category

Frontend Pages
- Dashboard: Summary of spending, budget vs actual, recent transactions
- Transactions: List and manage all transactions
- Budgets: View and edit monthly budgets by category
- Reports: Generate spending reports by category and time
- Analytics: Visual charts and trends for spending patterns

Deployment
Build the frontend:
cd frontend
npm run build

Serve the static files with Express (see backend/server.js for example).

Contributing
Pull requests are welcome. For major changes, please open an issue first.

License
MIT