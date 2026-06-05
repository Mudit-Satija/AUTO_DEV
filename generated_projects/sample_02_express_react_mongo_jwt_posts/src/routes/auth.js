const express = require('express');
const router = express.Router();
const { getUserByEmail, createUser } = require('../models/users');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const config = require('../config');

router.post('/register', async (req, res, next) => {
  const { username, email, password } = req.body;

  if (!username || !email || !password) {
    return res.status(400).json({ message: 'Username, email, and password are required' });
  }

  try {
    const existingUser = await getUserByEmail(email);
    if (existingUser) {
      return res.status(409).json({ message: 'Email already in use' });
    }

    const user = await createUser(username, email, password);
    const token = jwt.sign({ id: user.id, email: user.email }, config.jwt.secret, { expiresIn: config.jwt.expiresIn });

    res.status(201).json({
      message: 'User registered successfully',
      user: { id: user.id, username: user.username, email: user.email },
      token
    });
  } catch (err) {
    next(err);
  }
});

router.post('/login', async (req, res, next) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required' });
  }

  try {
    const user = await getUserByEmail(email);
    if (!user) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    const token = jwt.sign({ id: user.id, email: user.email }, config.jwt.secret, { expiresIn: config.jwt.expiresIn });

    res.json({
      message: 'Login successful',
      user: { id: user.id, username: user.username, email: user.email },
      token
    });
  } catch (err) {
    next(err);
  }
});

router.post('/logout', (req, res) => {
  res.json({ message: 'Logged out successfully' });
});

module.exports = router;