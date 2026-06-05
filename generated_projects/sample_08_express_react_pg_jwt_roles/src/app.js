const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { authenticateToken } = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const pool = require('./config/database');

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api', require('./routes/index'));

app.use(errorHandler);

module.exports = app;