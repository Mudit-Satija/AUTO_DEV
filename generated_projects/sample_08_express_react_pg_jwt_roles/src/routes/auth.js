const express = require('express');
const router = express.Router();
const pool = require('../config/database');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

// Register new user
router.post('/register', async (req, res) => {
  const { username, email, password, roleId } = req.body;

  if (!username || !email || !password) {
    return res.status(400).json({ message: 'Username, email, and password are required' });
  }

  try {
    const existingUser = await pool.query('SELECT id FROM users WHERE email = $1', [email]);
    if (existingUser.rows.length > 0) {
      return res.status(409).json({ message: 'Email already in use' });
    }

    const user = await pool.query(
      'INSERT INTO users (username, email, password_hash, role_id) VALUES ($1, $2, $3, $4) RETURNING id, username, email, role_id',
      [username, email, await bcrypt.hash(password, 10), roleId || 1]
    );

    const token = jwt.sign(
      { userId: user.rows[0].id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN }
    );

    res.status(201).json({
      message: 'User registered successfully',
      user: { id: user.rows[0].id, username: user.rows[0].username, email: user.rows[0].email, role_id: user.rows[0].role_id },
      token,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

// Login user
router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required' });
  }

  try {
    const user = await pool.query('SELECT id, username, email, password_hash, role_id FROM users WHERE email = $1', [email]);
    if (user.rows.length === 0) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const isValidPassword = await bcrypt.compare(password, user.rows[0].password_hash);
    if (!isValidPassword) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const token = jwt.sign(
      { userId: user.rows[0].id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN }
    );

    res.json({
      message: 'Login successful',
      user: { id: user.rows[0].id, username: user.rows[0].username, email: user.rows[0].email, role_id: user.rows[0].role_id },
      token,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

// Logout (client-side token removal; server-side no-op for stateless JWT)
router.post('/logout', (req, res) => {
  res.json({ message: 'Logout successful' });
});

module.exports = router;