require('dotenv').config();

const express = require('express');
const cors = require('cors');
const config = require('./config/index');
const connectDB = require('./config/database');
const errorHandler = require('./middleware/errorHandler');
const router = require('./routes/index');

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api', router);

connectDB().then(() => {
  app.listen(config.PORT, () => {
    console.log(`Server running on port ${config.PORT}`);
  });
});

app.use(errorHandler);