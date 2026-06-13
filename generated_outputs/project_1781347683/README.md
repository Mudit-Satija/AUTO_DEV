# ExpenseFlow

ExpenseFlow is a full-stack expense management application built with Express.js, React, and MongoDB. It enables users to track transactions, manage budgets, and analyze spending patterns across categories.

## Features

- **Dashboard**: Overview of current spending, budget status, and recent transactions
- **Transactions**: Add, view, edit, and delete expense transactions
- **Budgets**: Set and monitor monthly budgets by category
- **Reports**: Generate detailed spending reports by time period and category
- **Analytics**: Visualize spending trends with interactive charts and metrics

## Tech Stack

- **Backend**: Express.js
- **Frontend**: React (Vite)
- **Database**: MongoDB (Mongoose ODM)
- **SRS Entities**: Transaction, Budget, Category
- **SRS Pages**: Dashboard, Transactions, Budgets, Reports, Analytics

## Setup Instructions

### Prerequisites

- Node.js (v18+)
- MongoDB (local or cloud instance)
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the backend root:
```
MONGO_URI=mongodb://localhost:27017/expenseflow
PORT=5000
```

4. Start the Express server:
```bash
npm start
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm run dev
```

### Database

The application uses MongoDB to store:
- Transaction documents (amount, date, category, description)
- Budget documents (category, amount, month, year)
- Category documents (name, type)

Collections are automatically created on first use.

### API Endpoints

- `GET /api/transactions` - Get all transactions
- `POST /api/transactions` - Create a transaction
- `PUT /api/transactions/:id` - Update a transaction
- `DELETE /api/transactions/:id` - Delete a transaction
- `GET /api/budgets` - Get all budgets
- `POST /api/budgets` - Create a budget
- `PUT /api/budgets/:id` - Update a budget
- `DELETE /api/budgets/:id` - Delete a budget
- `GET /api/categories` - Get all categories

### Usage

1. Start the backend server
2. Start the frontend development server
3. Open http://localhost:5173 in your browser
4. Use the navigation bar to switch between Dashboard, Transactions, Budgets, Reports, and Analytics pages

All data is fetched from the backend API on page load. No local storage is used for persistent data.