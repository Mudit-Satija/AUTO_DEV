const express = require('express');
const config = require('./config/index');
const connectDB = require('./config/database');
const authRoutes = require('./routes/auth');
const authenticateToken = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const apiRoutes = require('./routes/index');

const app = express();

connectDB();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api/auth', authRoutes);

app.use('/api', authenticateToken, apiRoutes);

app.use(errorHandler);

const PORT = config.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});