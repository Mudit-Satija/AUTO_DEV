const express = require('express');
const config = require('./config/index');
const { connectDB } = require('./config/database');
const authRouter = require('./routes/auth');
const authenticateToken = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const apiRouter = require('./routes/index');

const app = express();

connectDB();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api/auth', authRouter);

app.use('/api', authenticateToken, apiRouter);

app.use(errorHandler);

const PORT = config.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});