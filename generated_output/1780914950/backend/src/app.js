require('dotenv').config();

const express = require('express');
const cors = require('cors');
const config = require('./config/index');
const { connectDB } = require('./config/database');
const errorHandler = require('./middleware/errorHandler');
const router = require('./routes/index');

const app = express();
const PORT = config.PORT;

app.use(cors());
app.use(express.json());
app.use('/api', router);
app.use(errorHandler);

connectDB().then(() => {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
});