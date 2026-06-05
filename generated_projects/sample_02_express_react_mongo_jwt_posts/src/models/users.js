const { Pool } = require('pg');
const bcrypt = require('bcrypt');
const config = require('../config');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  database: config.db.database,
  user: config.db.user,
  password: config.db.password
});

const getUserByEmail = async (email) => {
  const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
  return result.rows[0];
};

const getUserById = async (id) => {
  const result = await pool.query('SELECT id, username, email, created_at FROM users WHERE id = $1', [id]);
  return result.rows[0];
};

const createUser = async (username, email, password) => {
  const hashedPassword = await bcrypt.hash(password, 10);
  const result = await pool.query(
    'INSERT INTO users (username, email, password, created_at) VALUES ($1, $2, $3, NOW()) RETURNING id, username, email, created_at',
    [username, email, hashedPassword]
  );
  return result.rows[0];
};

module.exports = {
  getUserByEmail,
  getUserById,
  createUser
};