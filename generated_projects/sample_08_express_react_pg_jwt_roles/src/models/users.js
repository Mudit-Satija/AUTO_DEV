const pool = require('../config/database');
const bcrypt = require('bcrypt');

const getAllUsers = async () => {
  const result = await pool.query('SELECT id, username, email, role_id, created_at FROM users');
  return result.rows;
};

const getUserById = async (id) => {
  const result = await pool.query('SELECT id, username, email, role_id, created_at FROM users WHERE id = $1', [id]);
  return result.rows[0];
};

const getUserByEmail = async (email) => {
  const result = await pool.query('SELECT id, username, email, password_hash, role_id, created_at FROM users WHERE email = $1', [email]);
  return result.rows[0];
};

const createUser = async (username, email, password, roleId) => {
  const hashedPassword = await bcrypt.hash(password, 10);
  const result = await pool.query(
    'INSERT INTO users (username, email, password_hash, role_id) VALUES ($1, $2, $3, $4) RETURNING id, username, email, role_id, created_at',
    [username, email, hashedPassword, roleId]
  );
  return result.rows[0];
};

module.exports = {
  getAllUsers,
  getUserById,
  getUserByEmail,
  createUser,
};