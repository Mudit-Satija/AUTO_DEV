require('dotenv').config();

const express = require('express');
const cors = require('cors');
const { connectDB } = require('./config/database');
const config = require('./config/index');
const authRouter = require('./routes/auth');
const apiRouter = require('./routes/index');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = config.PORT;

app.use(cors());
app.use(express.json());

app.use('/api/auth', authRouter);
app.use('/api', apiRouter);

app.use(errorHandler);

connectDB().then(() => app.listen(PORT, () => console.log(`Server running on port ${PORT}`)));