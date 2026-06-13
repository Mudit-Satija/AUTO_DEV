ShopManager

A full-stack e-commerce management system built with Express.js, React, and MongoDB. Track products and orders in real time through an intuitive dashboard and dedicated views.

Features
- Manage products: create, read, update, delete
- Monitor orders: view order history and status
- Real-time dashboard with analytics
- RESTful API backend with MongoDB persistence
- Responsive React frontend with routing

Prerequisites
- Node.js (v18+)
- MongoDB (local or cloud instance)
- npm or yarn

Backend Setup
1. Navigate to the project root:
   cd ShopManager

2. Install backend dependencies:
   cd backend
   npm install

3. Create a .env file in backend/ with:
   MONGO_URI=mongodb://localhost:27017/shopmanager
   PORT=5000

4. Start the Express server:
   npm start

Frontend Setup
1. Navigate to frontend directory:
   cd frontend

2. Install frontend dependencies:
   npm install

3. Start the Vite dev server:
   npm run dev

Project Structure
backend/
├── app.js             # Express app entry point
├── routes/
│   └── index.js       # Aggregates product and order routes
├── controllers/
│   ├── product.js     # Product CRUD logic
│   └── order.js       # Order CRUD logic
├── models/
│   ├── Product.js     # Mongoose schema for Product
│   └── Order.js       # Mongoose schema for Order
├── config/
│   └── db.js          # MongoDB connection setup
└── .env               # Environment variables

frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx   # Dashboard view with analytics
│   │   ├── Products.jsx    # Product management UI
│   │   └── Orders.jsx      # Order tracking UI
│   ├── App.jsx             # Main router with navigation
│   ├── main.jsx            # Entry point
│   └── index.css
└── vite.config.js

API Endpoints
GET    /api/products     - List all products
POST   /api/products     - Create a new product
GET    /api/products/:id - Get product by ID
PUT    /api/products/:id - Update product
DELETE /api/products/:id - Delete product

GET    /api/orders       - List all orders
POST   /api/orders       - Create a new order
GET    /api/orders/:id   - Get order by ID
PUT    /api/orders/:id   - Update order
DELETE /api/orders/:id   - Delete order

Database Schema
Product:
- name: String (required)
- price: Number (required)
- description: String
- stock: Number (default: 0)
- createdAt: Date

Order:
- productId: ObjectId (ref: Product, required)
- quantity: Number (required)
- customerName: String (required)
- status: String (default: 'pending')
- createdAt: Date

Usage
1. Start backend server: npm start in backend/
2. Start frontend dev server: npm run dev in frontend/
3. Open http://localhost:5173 in your browser
4. Use the navigation bar to switch between Dashboard, Products, and Orders pages

All data is fetched from the backend API on page load — no localStorage is used.

Testing
Run backend tests with:
npm test

Run frontend tests with:
npm test -- --watchAll

Deployment
Build frontend:
cd frontend
npm run build

Serve static files with Express or deploy to Vercel/Netlify.

Connect to MongoDB Atlas or local instance via MONGO_URI.

Contributing
Pull requests are welcome. For major changes, open an issue first.

License
MIT