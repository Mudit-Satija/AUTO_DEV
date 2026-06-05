const express = require('express');
const router = express.Router();
const { Pool } = require('../config/database');

const pool = new Pool();

router.post('/', async (req, res) => {
  const { name, email, phone, event_id } = req.body;

  if (!name || !email || !event_id) {
    return res.status(400).json({ error: 'Name, email, and event_id are required' });
  }

  try {
    const client = await pool.connect();
    const result = await client.query(
      'INSERT INTO registrations (name, email, phone, event_id, created_at) VALUES ($1, $2, $3, $4, NOW()) RETURNING *',
      [name, email, phone, event_id]
    );
    client.release();
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/', async (req, res) => {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT * FROM registrations ORDER BY created_at DESC');
    client.release();
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const client = await pool.connect();
    const result = await client.query('SELECT * FROM registrations WHERE id = $1', [id]);
    client.release();

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Registration not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.put('/:id', async (req, res) => {
  const { id } = req.params;
  const { name, email, phone, event_id } = req.body;

  if (!name || !email || !event_id) {
    return res.status(400).json({ error: 'Name, email, and event_id are required' });
  }

  try {
    const client = await pool.connect();
    const result = await client.query(
      'UPDATE registrations SET name = $1, email = $2, phone = $3, event_id = $4, updated_at = NOW() WHERE id = $5 RETURNING *',
      [name, email, phone, event_id, id]
    );
    client.release();

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Registration not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.delete('/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const client = await pool.connect();
    const result = await client.query('DELETE FROM registrations WHERE id = $1 RETURNING *', [id]);
    client.release();

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Registration not found' });
    }

    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;