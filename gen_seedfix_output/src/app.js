const express = require('express');
const app = express();
const config = require('./config/index');
const connectDB = require('./config/database');
const errorHandler = require('./middleware/errorHandler');
const routes = require('./routes/index');

connectDB();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(require('cors')());

app.use('/api', routes);

app.use(errorHandler);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});