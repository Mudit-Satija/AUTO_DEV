const { Pool } = require('pg');
const config = require('../config');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  database: config.db.database,
  user: config.db.user,
  password: config.db.password
});

const getAllPosts = async () => {
  const result = await pool.query(
    'SELECT p.*, u.username AS author FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC'
  );
  return result.rows;
};

const getPostById = async (id) => {
  const result = await pool.query(
    'SELECT p.*, u.username AS author FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = $1',
    [id]
  );
  return result.rows[0];
};

const createPost = async (userId, title, content) => {
  const result = await pool.query(
    'INSERT INTO posts (user_id, title, content, created_at) VALUES ($1, $2, $3, NOW()) RETURNING *',
    [userId, title, content]
  );
  return result.rows[0];
};

const updatePost = async (id, userId, title, content) => {
  const result = await pool.query(
    'UPDATE posts SET title = $1, content = $2, updated_at = NOW() WHERE id = $3 AND user_id = $4 RETURNING *',
    [title, content, id, userId]
  );
  return result.rows[0];
};

const deletePost = async (id, userId) => {
  const result = await pool.query(
    'DELETE FROM posts WHERE id = $1 AND user_id = $2 RETURNING id',
    [id, userId]
  );
  return result.rowCount > 0;
};

module.exports = {
  getAllPosts,
  getPostById,
  createPost,
  updatePost,
  deletePost
};