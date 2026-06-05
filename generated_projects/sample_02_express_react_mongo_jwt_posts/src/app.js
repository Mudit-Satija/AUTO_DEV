const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const config = require('./config/database');
const mongodb = require('./config/mongodb');
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const routes = require('./routes');

const app = express();

// Middleware
app.use(cors());
app.use(helmet());
app.use(morgan('dev'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Connect to databases
mongodb.connect();

// Auth middleware
app.use('/api', authMiddleware);

// Routes
app.use('/api', routes);

// Error handler
app.use(errorHandler);

module.exports = app;