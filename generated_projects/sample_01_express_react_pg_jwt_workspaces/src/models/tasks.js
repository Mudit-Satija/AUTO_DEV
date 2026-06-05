const { Pool } = require('pg');
const config = require('../config/index');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  user: config.db.user,
  password: config.db.password,
  database: config.db.database,
});

const getTasks = async () => {
  const result = await pool.query('SELECT * FROM tasks ORDER BY id');
  return result.rows;
};

const getTaskById = async (id) => {
  const result = await pool.query('SELECT * FROM tasks WHERE id = $1', [id]);
  return result.rows[0];
};

const createTask = async (title, description, project_id, assigned_to, status) => {
  const result = await pool.query(
    'INSERT INTO tasks (title, description, project_id, assigned_to, status, created_at) VALUES ($1, $2, $3, $4, $5, NOW()) RETURNING *',
    [title, description, project_id, assigned_to, status]
  );
  return result.rows[0];
};

const updateTask = async (id, title, description, assigned_to, status) => {
  const result = await pool.query(
    'UPDATE tasks SET title = $1, description = $2, assigned_to = $3, status = $4, updated_at = NOW() WHERE id = $5 RETURNING *',
    [title, description, assigned_to, status, id]
  );
  return result.rows[0];
};

const deleteTask = async (id) => {
  const result = await pool.query('DELETE FROM tasks WHERE id = $1 RETURNING *', [id]);
  return result.rows[0];
};

module.exports = {
  getTasks,
  getTaskById,
  createTask,
  updateTask,
  deleteTask,
};