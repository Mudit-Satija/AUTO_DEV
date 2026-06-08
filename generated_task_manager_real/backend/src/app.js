const express = require('express');
const config = require('./config/index');
const connectDB = require('./config/database');
const errorHandler = require('./middleware/errorHandler');
const routes = require('./routes/index');

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api', routes);

app.use(errorHandler);

connectDB().catch(err => {
  console.error('Database connection failed, starting without DB:', err.message);
});

app.listen(config.PORT, () => {
  console.log(`Server running on port ${config.PORT}`);
});