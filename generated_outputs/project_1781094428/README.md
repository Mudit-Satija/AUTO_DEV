ShopManager

A full-stack e-commerce management system built with Express.js, React, and MongoDB. Manage products and orders through a clean web interface with real-time data synchronization.

Features
- RESTful API backend with Express.js
- React frontend with React Router for navigation
- MongoDB for persistent storage of Products and Orders
- Dashboard overview with key metrics
- Products management page
- Orders management page

Prerequisites
- Node.js (v18+)
- MongoDB (local or cloud instance)
- npm or yarn

Installation

1. Clone the repository:
   git clone https://github.com/yourusername/ShopManager.git
   cd ShopManager

2. Install backend dependencies:
   cd backend
   npm install

3. Install frontend dependencies:
   cd ../frontend
   npm install

4. Set up MongoDB connection:
   Create a .env file in the backend directory:
   MONGO_URI=mongodb://localhost:27017/shopmanager

   Replace the URI with your MongoDB connection string if using Atlas or another host.

5. Start the backend server:
   cd backend
   npm start

6. Start the frontend development server:
   cd frontend
   npm run dev

Directory Structure

backend/
├── app.js              # Express app entry point
├── routes/
│   └── index.js        # Aggregates all API routes
├── controllers/
│   ├── product.js      # Product route handlers
│   └── order.js        # Order route handlers
├── models/
│   ├── Product.js      # Mongoose schema for Product
│   └── Order.js        # Mongoose schema for Order
├── config/
│   └── db.js           # MongoDB connection setup
└── .env                # Environment variables

frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx   # Dashboard view
│   │   ├── Products.jsx    # Products management view
│   │   └── Orders.jsx      # Orders management view
│   ├── App.jsx             # Main router component
│   ├── main.jsx            # React root entry point
│   └── index.css           # Global styles
├── vite.config.js
└── package.json

API Endpoints

GET    /api/products     - Get all products
POST   /api/products     - Create a new product
GET    /api/products/:id - Get product by ID
PUT    /api/products/:id - Update product by ID
DELETE /api/products/:id - Delete product by ID

GET    /api/orders       - Get all orders
POST   /api/orders       - Create a new order
GET    /api/orders/:id   - Get order by ID
PUT    /api/orders/:id   - Update order by ID
DELETE /api/orders/:id   - Delete order by ID

Frontend Pages

Dashboard.jsx - Displays summary statistics (total products, total orders, revenue)
Products.jsx  - Lists all products with create, edit, delete actions
Orders.jsx    - Lists all orders with status and customer details

Usage

After starting both servers, open http://localhost:5173 in your browser.

The navigation bar at the top allows switching between Dashboard, Products, and Orders pages. All data is fetched live from the backend API — no local storage is used.

Troubleshooting

- If you get a connection error, ensure MongoDB is running and MONGO_URI is correct.
- If the frontend doesn't load, ensure the backend is running on http://localhost:5000 (default).
- Clear browser cache if you see stale UI after updates.

License
MIT