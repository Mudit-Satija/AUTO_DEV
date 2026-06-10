ShopManager

A full-stack e-commerce management system built with Express.js, React, and MongoDB. Manage products and orders through a clean web interface with real-time backend synchronization.

Backend Features:
- RESTful API endpoints for Product and Order entities
- MongoDB/Mongoose data modeling
- Express.js middleware for request handling
- CORS-enabled API server

Frontend Features:
- React frontend with Vite build tool
- Navigation between Dashboard, Products, and Orders pages
- Real-time data fetching from backend API
- No localStorage usage — all state comes from backend

Database Schema:
- Product: { name, price, description, stock, createdAt }
- Order: { customerId, items, total, status, createdAt }

Setup Instructions

1. Clone the repository
   git clone https://github.com/yourusername/ShopManager.git
   cd ShopManager

2. Install backend dependencies
   cd backend
   npm install

3. Install frontend dependencies
   cd ../frontend
   npm install

4. Start MongoDB
   Ensure MongoDB is running locally (e.g., mongod)

5. Start the backend server
   cd backend
   npm start

6. Start the frontend development server
   cd ../frontend
   npm run dev

7. Open your browser to http://localhost:5173

Project Structure

backend/
├── app.js              # Express app entry point
├── routes/
│   └── index.js        # Aggregates product and order routes
├── controllers/
│   ├── product.js      # Product route handlers
│   └── order.js        # Order route handlers
├── models/
│   ├── Product.js      # Mongoose schema for Product
│   └── Order.js        # Mongoose schema for Order
├── config/
│   └── db.js           # MongoDB connection setup
└── server.js           # Server startup (optional, if used)

frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx   # Dashboard view
│   │   ├── Products.jsx    # Products management view
│   │   └── Orders.jsx      # Orders management view
│   ├── App.jsx             # Main app router with navigation
│   ├── main.jsx            # React root entry point
│   └── index.css           # Global styles
├── vite.config.js
└── package.json

Environment Variables

Create a .env file in the backend folder:

MONGODB_URI=mongodb://localhost:27017/shopmanager
PORT=5000

The backend will connect to MongoDB using MONGODB_URI and listen on PORT.

Notes

- All frontend pages fetch data directly from the backend API on mount.
- No client-side state persistence using localStorage — data is always fresh from the server.
- Routes are aggregated in backend/routes/index.js and mounted under /api.
- Frontend uses React Router for navigation between Dashboard, Products, and Orders.

Testing

After setup, test endpoints:

GET http://localhost:5000/api/products
GET http://localhost:5000/api/orders

Frontend navigation is accessible via the header bar on http://localhost:5173