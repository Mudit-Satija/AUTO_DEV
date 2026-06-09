const express = require('express');
const router = express.Router();
const User = require('../models/users');
const auth = require('../middleware/auth');

router.use(auth);

router.get('/', async (req, res) => {
  try {
    const users = await User.find({}, 'email createdAt');
    res.json(users);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.get('/me', async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    res.json(user);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.put('/me', async (req, res) => {
  const { email } = req.body;

  try {
    const user = await User.findById(req.user.id);
    if (!user) return res.status(404).json({ message: 'User not found' });

    if (email) {
      const existingUser = await User.findOne({ email });
      if (existingUser && existingUser._id.toString() !== req.user.id.toString()) {
        return res.status(400).json({ message: 'Email already in use' });
      }
      user.email = email;
    }

    const updatedUser = await user.save();
    res.json({ id: updatedUser._id, email: updatedUser.email });
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

module.exports = router;