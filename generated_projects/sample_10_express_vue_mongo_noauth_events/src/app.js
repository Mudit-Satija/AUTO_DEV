const express = require('express');
const config = require('./config/database');
const mongodb = require('./config/mongodb');
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const routes = require('./routes/index');

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api', authMiddleware, routes);

app.use(errorHandler);

module.exports = app;