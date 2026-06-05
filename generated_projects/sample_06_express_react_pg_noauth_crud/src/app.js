const express = require('express');
const cors = require('cors');
const path = require('path');
const pool = require('../config/database');
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');

const app = express();

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

app.use('/api', authMiddleware, require('./routes'));

app.use(errorHandler);

module.exports = app;