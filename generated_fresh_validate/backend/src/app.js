const express = require('express');
const cors = require('cors');
const config = require('./config/index');
const connectDB = require('./config/database');
const authRouter = require('./routes/auth');
const errorHandler = require('./middleware/errorHandler');
const apiRouter = require('./routes/index');

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api/auth', authRouter);
app.use('/api', apiRouter);

app.use(errorHandler);

connectDB().then(() => {
  app.listen(config.PORT, () => {
    console.log(`Server running on port ${config.PORT}`);
  });
}).catch(err => {
  console.error('Database connection error:', err);
  process.exit(1);
});