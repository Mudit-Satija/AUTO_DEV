const express = require('express');
const pool = require('../config/db');

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM projects WHERE user_id = $1', [req.user.id]);
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error fetching projects.' });
  }
});

router.post('/', async (req, res) => {
  const { name, description } = req.body;

  if (!name) {
    return res.status(400).json({ message: 'Project name is required.' });
  }

  try {
    const result = await pool.query(
      'INSERT INTO projects (name, description, user_id) VALUES ($1, $2, $3) RETURNING *',
      [name, description, req.user.id]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error creating project.' });
  }
});

router.put('/:id', async (req, res) => {
  const { id } = req.params;
  const { name, description } = req.body;

  if (!name) {
    return res.status(400).json({ message: 'Project name is required.' });
  }

  try {
    const result = await pool.query(
      'UPDATE projects SET name = $1, description = $2 WHERE id = $3 AND user_id = $4 RETURNING *',
      [name, description, id, req.user.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Project not found or not authorized.' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error updating project.' });
  }
});

router.delete('/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query(
      'DELETE FROM projects WHERE id = $1 AND user_id = $2 RETURNING *',
      [id, req.user.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Project not found or not authorized.' });
    }

    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error deleting project.' });
  }
});

module.exports = router;