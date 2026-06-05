const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const config = require('./config');
const authMiddleware = require('./middleware/auth');
const authRoutes = require('./routes/auth');
const projectRoutes = require('./routes/projects');
const taskRoutes = require('./routes/tasks');
const errorHandler = require('./middleware/errorHandler');

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api/auth', authRoutes);
app.use('/api/projects', authMiddleware, projectRoutes);
app.use('/api/tasks', authMiddleware, taskRoutes);

app.use(errorHandler);

module.exports = app;