const { Pool } = require('pg');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const config = require('../config/index');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  user: config.db.user,
  password: config.db.password,
  database: config.db.database,
});

const findUserByEmail = async (email) => {
  const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
  return result.rows[0];
};

const createUser = async (name, email, password) => {
  const hashedPassword = await bcrypt.hash(password, 10);
  const result = await pool.query(
    'INSERT INTO users (name, email, password, created_at) VALUES ($1, $2, $3, NOW()) RETURNING *',
    [name, email, hashedPassword]
  );
  return result.rows[0];
};

const generateToken = (user) => {
  return jwt.sign({ id: user.id, email: user.email }, config.jwt.secret, {
    expiresIn: config.jwt.expiresIn,
  });
};

const verifyPassword = async (password, hashedPassword) => {
  return bcrypt.compare(password, hashedPassword);
};

module.exports = {
  findUserByEmail,
  createUser,
  generateToken,
  verifyPassword,
};