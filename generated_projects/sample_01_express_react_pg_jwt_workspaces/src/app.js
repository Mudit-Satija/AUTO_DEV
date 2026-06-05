const express = require('express');
const config = require('./config/index');
const db = require('./config/database');
const errorHandler = require('./middleware/errorHandler');
const authRoutes = require('./routes/auth');
const routes = require('./routes/index');
const authMiddleware = require('./middleware/auth');

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api/auth', authRoutes);
app.use('/api', authMiddleware, routes);

app.use(errorHandler);

const PORT = config.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;