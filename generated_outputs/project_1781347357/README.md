ExpenseFlow

A full-stack expense tracking application built with Express.js, React, and MongoDB. Track transactions, manage budgets, and analyze spending patterns across categories.

Features
- Real-time transaction logging with categories
- Monthly budget planning and tracking
- Interactive reports and analytics dashboards
- RESTful API backend with MongoDB persistence
- Responsive React frontend with client-side routing

Backend Structure
- Models: Transaction, Budget, Category (Mongoose schemas)
- Routes: /api/transactions, /api/budgets, /api/categories
- Database: MongoDB (connected via Mongoose)
- Server: Express.js with middleware for CORS, JSON parsing, and error handling

Frontend Structure
- Pages: Dashboard, Transactions, Budgets, Reports, Analytics
- State: Fetches all data from backend API on mount (no localStorage)
- Routing: React Router DOM with navigation header
- Styling: CSS modules or global styles (not specified — use clean, semantic CSS)

Setup Instructions

Prerequisites
- Node.js (v18+)
- MongoDB (local or Atlas)
- npm or yarn

1. Clone the repository
git clone https://github.com/yourusername/expenseflow.git
cd expenseflow

2. Install backend dependencies
cd backend
npm install

3. Install frontend dependencies
cd ../frontend
npm install

4. Configure environment variables

Create .env in backend/:
MONGO_URI=mongodb://localhost:27017/expenseflow
PORT=5000

Create .env in frontend/:
VITE_API_BASE_URL=http://localhost:5000/api

5. Start MongoDB
Ensure MongoDB is running locally or connect to MongoDB Atlas.

6. Start backend server
cd backend
npm start

7. Start frontend development server
cd frontend
npm run dev

8. Open browser to http://localhost:5173

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

Database Models

Transaction
- amount: Number (required)
- description: String (required)
- date: Date (required)
- category: ObjectId (ref: Category, required)
- type: String (enum: 'income', 'expense', required)

Budget
- category: ObjectId (ref: Category, required)
- amount: Number (required)
- month: String (format: YYYY-MM, required)
- year: Number (required)

Category
- name: String (required, unique)
- color: String (hex color code, optional)

Frontend Pages

Dashboard
- Shows summary: total income, total expenses, net balance
- Recent transactions list
- Current month’s budget vs spending

Transactions
- List all transactions with filters (date range, category, type)
- Form to add/edit/delete transactions

Budgets
- View and edit monthly budgets per category
- Visual indicator for budget utilization

Reports
- Pie chart: spending by category
- Bar chart: monthly trends
- Exportable data summaries

Analytics
- Advanced spending patterns
- Forecasting based on historical data
- Correlation insights between categories

Notes
- All pages fetch data from the backend on component mount.
- No client-side state persistence (localStorage) is used for entity data.
- Navigation is handled via React Router with a persistent header.
- Backend routes are mounted under /api.
- Mongoose is used for MongoDB interaction; no SQL or other ORMs.

Deployment
- Backend: Deploy to Node.js hosting (Render, Railway, Heroku)
- Frontend: Build with `npm run build` and deploy to Vercel, Netlify, or static hosting
- MongoDB: Use MongoDB Atlas for production

License
MIT