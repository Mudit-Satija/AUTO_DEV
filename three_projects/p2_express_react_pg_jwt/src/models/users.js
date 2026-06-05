const pool = require('../config/database');

const createUser = async (username, email, passwordHash) => {
  const query = `
    INSERT INTO users (username, email, password_hash, created_at)
    VALUES ($1, $2, $3, NOW())
    RETURNING id, username, email, created_at;
  `;
  const values = [username, email, passwordHash];
  const result = await pool.query(query, values);
  return result.rows[0];
};

const getUserById = async (id) => {
  const query = `
    SELECT id, username, email, created_at
    FROM users
    WHERE id = $1;
  `;
  const result = await pool.query(query, [id]);
  return result.rows[0];
};

const getUserByEmail = async (email) => {
  const query = `
    SELECT id, username, email, password_hash, created_at
    FROM users
    WHERE email = $1;
  `;
  const result = await pool.query(query, [email]);
  return result.rows[0];
};

const updateUser = async (id, username, email) => {
  const query = `
    UPDATE users
    SET username = $1, email = $2, updated_at = NOW()
    WHERE id = $3
    RETURNING id, username, email, updated_at;
  `;
  const values = [username, email, id];
  const result = await pool.query(query, values);
  return result.rows[0];
};

const deleteUser = async (id) => {
  const query = `
    DELETE FROM users
    WHERE id = $1
    RETURNING id;
  `;
  const result = await pool.query(query, [id]);
  return result.rows[0];
};

module.exports = {
  createUser,
  getUserById,
  getUserByEmail,
  updateUser,
  deleteUser
};