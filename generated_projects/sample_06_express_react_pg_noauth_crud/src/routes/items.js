const express = require('express');
const pool = require('../config/database');
const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM items ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM items WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Item not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const { name, category_id, description } = req.body;
    if (!name || !category_id) {
      return res.status(400).json({ error: 'Name and category_id are required' });
    }
    const categoryCheck = await pool.query('SELECT id FROM categories WHERE id = $1', [category_id]);
    if (categoryCheck.rows.length === 0) {
      return res.status(404).json({ error: 'Category not found' });
    }
    const result = await pool.query(
      'INSERT INTO items (name, category_id, description) VALUES ($1, $2, $3) RETURNING *',
      [name, category_id, description || null]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { name, category_id, description } = req.body;
    if (!name || !category_id) {
      return res.status(400).json({ error: 'Name and category_id are required' });
    }
    const categoryCheck = await pool.query('SELECT id FROM categories WHERE id = $1', [category_id]);
    if (categoryCheck.rows.length === 0) {
      return res.status(404).json({ error: 'Category not found' });
    }
    const result = await pool.query(
      'UPDATE items SET name = $1, category_id = $2, description = $3 WHERE id = $4 RETURNING *',
      [name, category_id, description || null, req.params.id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Item not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM items WHERE id = $1 RETURNING *', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Item not found' });
    }
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;