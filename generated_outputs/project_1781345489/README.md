ShopManager

A full-stack e-commerce management system built with Express.js, React, and MongoDB. Track products and orders in real-time through a clean, responsive dashboard.

Features
- Manage products: create, read, update, delete
- Monitor orders: view order history and status
- Real-time dashboard with analytics
- RESTful API backend with MongoDB persistence
- React frontend with routing and state management

Setup Instructions

Backend Setup
1. Navigate to the project root directory:
   cd ShopManager

2. Install backend dependencies:
   cd backend
   npm install

3. Start MongoDB (ensure it's running locally or update connection string in ./backend/config/db.js)

4. Start the Express server:
   node server.js

   The API will be available at http://localhost:5000/api

Frontend Setup
1. Navigate to the frontend directory:
   cd frontend

2. Install frontend dependencies:
   npm install

3. Start the React development server:
   npm run dev

   The frontend will be available at http://localhost:5173

Project Structure

backend/
├── server.js              # Express server entry point
├── config/
│   └── db.js              # MongoDB connection setup
├── routes/
│   ├── index.js           # Aggregates all API routes
│   ├── product.js         # Product CRUD routes
│   └── order.js           # Order CRUD routes
├── models/
│   ├── Product.js         # Mongoose schema for Product
│   └── Order.js           # Mongoose schema for Order
└── controllers/
    ├── productController.js # Product logic
    └── orderController.js   # Order logic

frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx  # Dashboard view
│   │   ├── Products.jsx   # Products management view
│   │   └── Orders.jsx     # Orders management view
│   ├── App.jsx            # Main routing component
│   ├── main.jsx           # React root entry point
│   └── index.css          # Global styles
├── vite.config.js
└── package.json

Environment Variables

Create a .env file in the backend directory:

MONGO_URI=mongodb://localhost:27017/shopmanager
PORT=5000

Database Models

Product Schema
- name: String (required)
- price: Number (required)
- stock: Number (required)
- description: String
- createdAt: Date

Order Schema
- productId: ObjectId (ref: Product, required)
- quantity: Number (required)
- total: Number (required)
- status: String (enum: pending, shipped, delivered, cancelled)
- customerName: String (required)
- customerEmail: String
- createdAt: Date

API Endpoints

GET /api/products           - Get all products
POST /api/products          - Create a new product
GET /api/products/:id       - Get product by ID
PUT /api/products/:id       - Update product by ID
DELETE /api/products/:id    - Delete product by ID

GET /api/orders             - Get all orders
POST /api/orders            - Create a new order
GET /api/orders/:id         - Get order by ID
PUT /api/orders/:id         - Update order by ID
DELETE /api/orders/:id      - Delete order by ID

Frontend Pages

Dashboard.jsx - Displays summary stats: total products, total orders, recent activity
Products.jsx - Table view with CRUD actions for products
Orders.jsx - Table view with CRUD actions for orders

Navigation
The App.jsx component renders a navigation bar with links to all three pages: Dashboard, Products, and Orders. All data is fetched from the backend API on component mount — no localStorage is used.

Testing
Run the backend tests with:
npm test

Run the frontend tests with:
npm run test

Deployment
For production, use a process manager like PM2 for the backend and build the frontend with:

cd frontend
npm run build

Then serve the static files from the ./frontend/dist directory with Express or a CDN.

License
MIT