const { Pool } = require('pg');
const config = require('../config/index');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  user: config.db.user,
  password: config.db.password,
  database: config.db.database,
});

const getProjects = async () => {
  const result = await pool.query('SELECT * FROM projects ORDER BY id');
  return result.rows;
};

const getProjectById = async (id) => {
  const result = await pool.query('SELECT * FROM projects WHERE id = $1', [id]);
  return result.rows[0];
};

const createProject = async (name, workspace_id, description) => {
  const result = await pool.query(
    'INSERT INTO projects (name, workspace_id, description, created_at) VALUES ($1, $2, $3, NOW()) RETURNING *',
    [name, workspace_id, description]
  );
  return result.rows[0];
};

const updateProject = async (id, name, description) => {
  const result = await pool.query(
    'UPDATE projects SET name = $1, description = $2, updated_at = NOW() WHERE id = $3 RETURNING *',
    [name, description, id]
  );
  return result.rows[0];
};

const deleteProject = async (id) => {
  const result = await pool.query('DELETE FROM projects WHERE id = $1 RETURNING *', [id]);
  return result.rows[0];
};

module.exports = {
  getProjects,
  getProjectById,
  createProject,
  updateProject,
  deleteProject,
};