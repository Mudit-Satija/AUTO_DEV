const express = require('express');
const router = express.Router();
const pool = require('../config/database');
const bcrypt = require('bcrypt');

router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT u.id, u.username, u.email, u.created_at, ARRAY_AGG(r.name) AS roles FROM users u LEFT JOIN user_roles ur ON u.id = ur.user_id LEFT JOIN roles r ON ur.role_id = r.id GROUP BY u.id, u.username, u.email, u.created_at ORDER BY u.username');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('SELECT u.id, u.username, u.email, u.created_at, ARRAY_AGG(r.name) AS roles FROM users u LEFT JOIN user_roles ur ON u.id = ur.user_id LEFT JOIN roles r ON ur.role_id = r.id WHERE u.id = $1 GROUP BY u.id, u.username, u.email, u.created_at', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/', async (req, res) => {
  try {
    const { username, email, password, role_ids } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required' });
    }

    const existingUser = await pool.query('SELECT id FROM users WHERE username = $1 OR email = $2', [username, email]);
    if (existingUser.rows.length > 0) {
      return res.status(409).json({ error: 'Username or email already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const result = await pool.query('INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3) RETURNING id, username, email, created_at', [username, email, hashedPassword]);
    const userId = result.rows[0].id;

    if (role_ids && Array.isArray(role_ids)) {
      const roleValues = role_ids.map(rid => `(${userId}, ${rid})`).join(',');
      if (roleValues) {
        await pool.query(`INSERT INTO user_roles (user_id, role_id) VALUES ${roleValues}`);
      }
    }

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { username, email, password, role_ids } = req.body;

    const existingUser = await pool.query('SELECT id FROM users WHERE (username = $1 OR email = $2) AND id != $3', [username, email, id]);
    if (existingUser.rows.length > 0) {
      return res.status(409).json({ error: 'Username or email already exists' });
    }

    let updatedFields = [];
    let values = [];
    let index = 1;

    if (username) {
      updatedFields.push(`username = $${index}`);
      values.push(username);
      index++;
    }
    if (email) {
      updatedFields.push(`email = $${index}`);
      values.push(email);
      index++;
    }
    if (password) {
      const hashedPassword = await bcrypt.hash(password, 10);
      updatedFields.push(`password_hash = $${index}`);
      values.push(hashedPassword);
      index++;
    }

    if (updatedFields.length === 0) {
      return res.status(400).json({ error: 'No fields to update' });
    }

    values.push(id);
    const updateQuery = `UPDATE users SET ${updatedFields.join(', ')} WHERE id = $${index} RETURNING id, username, email, created_at`;
    const result = await pool.query(updateQuery, values);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    await pool.query('DELETE FROM user_roles WHERE user_id = $1', [id]);
    if (role_ids && Array.isArray(role_ids)) {
      const roleValues = role_ids.map(rid => `(${id}, ${rid})`).join(',');
      if (roleValues) {
        await pool.query(`INSERT INTO user_roles (user_id, role_id) VALUES ${roleValues}`);
      }
    }

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('DELETE FROM users WHERE id = $1 RETURNING id', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;