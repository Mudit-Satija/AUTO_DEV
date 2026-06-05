const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const db = require('./config/database.js');
const authMiddleware = require('./middleware/auth.js');
const errorHandler = require('./middleware/errorHandler.js');
const routes = require('./routes/index.js');

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api/auth', require('./routes/auth.js'));
app.use(authMiddleware);
app.use('/api', routes);

app.use(errorHandler);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});