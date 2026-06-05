const pool = require('../config/database');

const getAllPermissions = async () => {
  const result = await pool.query('SELECT id, name, description FROM permissions');
  return result.rows;
};

const getPermissionById = async (id) => {
  const result = await pool.query('SELECT id, name, description FROM permissions WHERE id = $1', [id]);
  return result.rows[0];
};

const createPermission = async (name, description) => {
  const result = await pool.query(
    'INSERT INTO permissions (name, description) VALUES ($1, $2) RETURNING *',
    [name, description]
  );
  return result.rows[0];
};

module.exports = {
  getAllPermissions,
  getPermissionById,
  createPermission,
};