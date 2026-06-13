ExpenseFlow

A full-stack expense tracking application built with Express.js, React, and MongoDB. Track transactions, manage budgets, and analyze spending patterns with intuitive dashboards and reports.

Features
- Real-time transaction logging with categories
- Monthly budget planning and tracking
- Visual analytics and reporting
- Responsive dashboard with data visualization
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
1. Navigate to the project root
2. Install dependencies:
   npm install

3. Create a .env file in the root directory:
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/expenseflow

4. Start the Express server:
   npm run dev

Frontend Setup
1. Navigate to the client directory:
   cd client

2. Install dependencies:
   npm install

3. Start the React dev server:
   npm run dev

The frontend will automatically open at http://localhost:5173

API Endpoints
- GET /api/transactions — Get all transactions
- POST /api/transactions — Create a new transaction
- PUT /api/transactions/:id — Update a transaction
- DELETE /api/transactions/:id — Delete a transaction
- GET /api/budgets — Get all budgets
- POST /api/budgets — Create a new budget
- PUT /api/budgets/:id — Update a budget
- DELETE /api/budgets/:id — Delete a budget
- GET /api/categories — Get all categories
- POST /api/categories — Create a new category
- PUT /api/categories/:id — Update a category
- DELETE /api/categories/:id — Delete a category

Database Schema
Transaction:
- amount: Number
- description: String
- date: Date
- category: ObjectId (ref: Category)
- type: String (income/expense)

Budget:
- category: ObjectId (ref: Category)
- amount: Number
- month: Date
- year: Number

Category:
- name: String
- type: String (income/expense)
- color: String

Usage
1. Start both backend and frontend servers
2. Navigate to http://localhost:5173
3. Use the navigation bar to switch between Dashboard, Transactions, Budgets, Reports, and Analytics pages
4. Add, edit, or delete transactions and budgets as needed
5. View analytics and reports generated from your data

Note: All data is persisted in MongoDB. No data is stored in localStorage.

Deployment
For production:
1. Build the frontend:
   cd client
   npm run build

2. Serve the static files using Express (see server.js in backend for example)

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
MIT