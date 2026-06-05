const express = require('express');
const router = express.Router();
const pool = require('../config/database');

// GET /api/users - Get all users
router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT id, username, email, created_at FROM users ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/users/:id - Get user by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('SELECT id, username, email, created_at FROM users WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/users - Create a new user
router.post('/', async (req, res) => {
  try {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password are required' });
    }

    // Check if user already exists
    const existingUser = await pool.query('SELECT id FROM users WHERE email = $1 OR username = $2', [email, username]);
    if (existingUser.rows.length > 0) {
      return res.status(409).json({ error: 'User with this email or username already exists' });
    }

    const result = await pool.query(
      'INSERT INTO users (username, email, password, created_at) VALUES ($1, $2, $3, NOW()) RETURNING id, username, email, created_at',
      [username, email, password]
    );

    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/users/:id - Update a user
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { username, email } = req.body;

    if (!username && !email) {
      return res.status(400).json({ error: 'Username or email must be provided' });
    }

    const updateFields = [];
    const values = [];

    if (username) {
      updateFields.push('username = $' + (values.length + 1));
      values.push(username);
    }
    if (email) {
      updateFields.push('email = $' + (values.length + 1));
      values.push(email);
    }

    values.push(id);

    // Check if email is already taken by another user
    if (email) {
      const existingUser = await pool.query(
        'SELECT id FROM users WHERE email = $1 AND id != $2',
        [email, id]
      );
      if (existingUser.rows.length > 0) {
        return res.status(409).json({ error: 'Email is already in use by another user' });
      }
    }

    // Check if username is already taken by another user
    if (username) {
      const existingUser = await pool.query(
        'SELECT id FROM users WHERE username = $1 AND id != $2',
        [username, id]
      );
      if (existingUser.rows.length > 0) {
        return res.status(409).json({ error: 'Username is already in use by another user' });
      }
    }

    const query = `UPDATE users SET ${updateFields.join(', ')}, updated_at = NOW() WHERE id = $${values.length} RETURNING id, username, email, created_at`;

    const result = await pool.query(query, values);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error updating user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// DELETE /api/users/:id - Delete a user
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('DELETE FROM users WHERE id = $1 RETURNING id', [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.status(204).send();
  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;