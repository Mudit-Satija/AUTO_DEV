const express = require('express');
const config = require('./config/index');
const connectDB = require('./config/database');
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const authRoutes = require('./routes/auth');
const routes = require('./routes/index');

const app = express();

// Connect to MongoDB
connectDB();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(require('cors')());

// Mount auth routes (public)
app.use('/api/auth', authRoutes);

// Mount protected routes with auth middleware
app.use('/api', authMiddleware, routes);

// Global error handler
app.use(errorHandler);

// Start server
const PORT = config.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});