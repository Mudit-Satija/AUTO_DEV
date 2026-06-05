const pool = require('../config/database');

const getAllRoles = async () => {
  const result = await pool.query('SELECT id, name, description FROM roles');
  return result.rows;
};

const getRoleById = async (id) => {
  const result = await pool.query('SELECT id, name, description FROM roles WHERE id = $1', [id]);
  return result.rows[0];
};

const createRole = async (name, description) => {
  const result = await pool.query(
    'INSERT INTO roles (name, description) VALUES ($1, $2) RETURNING *',
    [name, description]
  );
  return result.rows[0];
};

module.exports = {
  getAllRoles,
  getRoleById,
  createRole,
};