require('dotenv').config();

const express = require('express');
const cors = require('cors');
const { connectDB } = require('./config/database');
const authRouter = require('./routes/auth');
const router = require('./routes/index');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.use('/api/auth', authRouter);
app.use('/api', router);

app.use(errorHandler);

connectDB().then(() => app.listen(PORT, () => console.log(`Server running on port ${PORT}`)));