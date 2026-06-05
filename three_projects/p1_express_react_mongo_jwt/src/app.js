const express = require('express');
const config = require('./config/index');
const connectDB = require('./config/database');
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const routes = require('./routes/index');

const app = express();

// Initialize config
config();

// Connect to MongoDB
connectDB();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(require('cors')());

// Mount auth routes
app.use('/api/auth', require('./routes/auth'));

// Apply auth middleware to all routes under /api except /api/auth
app.use('/api', authMiddleware);

// Mount protected module routes
app.use('/api', routes);

// Global error handler
app.use(errorHandler);

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});