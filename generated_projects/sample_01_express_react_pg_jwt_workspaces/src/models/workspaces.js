const { Pool } = require('pg');
const config = require('../config/index');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  user: config.db.user,
  password: config.db.password,
  database: config.db.database,
});

const getWorkspaces = async () => {
  const result = await pool.query('SELECT * FROM workspaces ORDER BY id');
  return result.rows;
};

const getWorkspaceById = async (id) => {
  const result = await pool.query('SELECT * FROM workspaces WHERE id = $1', [id]);
  return result.rows[0];
};

const createWorkspace = async (name, description) => {
  const result = await pool.query(
    'INSERT INTO workspaces (name, description, created_at) VALUES ($1, $2, NOW()) RETURNING *',
    [name, description]
  );
  return result.rows[0];
};

const updateWorkspace = async (id, name, description) => {
  const result = await pool.query(
    'UPDATE workspaces SET name = $1, description = $2, updated_at = NOW() WHERE id = $3 RETURNING *',
    [name, description, id]
  );
  return result.rows[0];
};

const deleteWorkspace = async (id) => {
  const result = await pool.query('DELETE FROM workspaces WHERE id = $1 RETURNING *', [id]);
  return result.rows[0];
};

module.exports = {
  getWorkspaces,
  getWorkspaceById,
  createWorkspace,
  updateWorkspace,
  deleteWorkspace,
};