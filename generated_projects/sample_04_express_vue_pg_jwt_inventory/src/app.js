const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const pool = require('./config/database');

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

// Auth middleware
const authenticateJWT = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'Access token required' });

  const token = authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Access token required' });

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid or expired token' });
    req.user = user;
    next();
  });
};

// Import routes
const authRoutes = require('./routes/auth');
const customersRoutes = require('./routes/customers');
const inventoryRoutes = require('./routes/inventory');
const ordersRoutes = require('./routes/orders');

// Mount routes
app.use('/api/auth', authRoutes);
app.use('/api/customers', authenticateJWT, customersRoutes);
app.use('/api/inventory', authenticateJWT, inventoryRoutes);
app.use('/api/orders', authenticateJWT, ordersRoutes);

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

module.exports = app;