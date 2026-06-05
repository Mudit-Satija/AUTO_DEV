const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const mongoose = require('mongoose');
const authMiddleware = require('./middleware/auth.js');
const errorHandler = require('./middleware/errorHandler.js');
const authRoutes = require('./routes/auth.js');
const apiRoutes = require('./routes/index.js');

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

// Database connection
require('./config/database.js');

// Mount auth routes (public)
app.use('/api/auth', authRoutes);

// Mount protected routes with auth middleware
app.use('/api', authMiddleware, apiRoutes);

// Error handler
app.use(errorHandler);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});