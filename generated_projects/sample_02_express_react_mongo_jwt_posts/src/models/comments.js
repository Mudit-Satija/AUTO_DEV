const { Pool } = require('pg');
const config = require('../config');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  database: config.db.database,
  user: config.db.user,
  password: config.db.password
});

const getCommentsByPostId = async (postId) => {
  const result = await pool.query(
    'SELECT * FROM comments WHERE post_id = $1 ORDER BY created_at DESC',
    [postId]
  );
  return result.rows;
};

const createComment = async (postId, userId, content) => {
  const result = await pool.query(
    'INSERT INTO comments (post_id, user_id, content, created_at) VALUES ($1, $2, $3, NOW()) RETURNING *',
    [postId, userId, content]
  );
  return result.rows[0];
};

const deleteComment = async (commentId, userId) => {
  const result = await pool.query(
    'DELETE FROM comments WHERE id = $1 AND user_id = $2 RETURNING id',
    [commentId, userId]
  );
  return result.rowCount > 0;
};

module.exports = {
  getCommentsByPostId,
  createComment,
  deleteComment
};