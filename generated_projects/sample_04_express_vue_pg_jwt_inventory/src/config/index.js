const dotenv = require('dotenv');

dotenv.config();

const pool = require('./database');

module.exports = {
  pool,
  jwtSecret: process.env.JWT_SECRET,
  jwtExpiresIn: process.env.JWT_EXPIRES_IN
};