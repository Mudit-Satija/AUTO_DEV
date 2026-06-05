const express = require('express');
const router = express.Router();
const pool = require('../config/database');

// GET /api/comments - Get all comments
router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM comments ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching comments:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/comments/:id - Get comment by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('SELECT * FROM comments WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Comment not found' });
    }
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching comment:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/comments - Create a new comment
router.post('/', async (req, res) => {
  try {
    const { content, author, post } = req.body;

    if (!content || !author || !post) {
      return res.status(400).json({ error: 'Content, author, and post are required' });
    }

    const result = await pool.query(
      'INSERT INTO comments (content, author, post, created_at) VALUES ($1, $2, $3, NOW()) RETURNING *',
      [content, author, post]
    );

    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error creating comment:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/comments/:id - Update a comment
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { content } = req.body;

    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const result = await pool.query(
      'UPDATE comments SET content = $1, updated_at = NOW() WHERE id = $2 RETURNING *',
      [content, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Comment not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error updating comment:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// DELETE /api/comments/:id - Delete a comment
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('DELETE FROM comments WHERE id = $1 RETURNING *', [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Comment not found' });
    }

    res.status(204).send();
  } catch (error) {
    console.error('Error deleting comment:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;