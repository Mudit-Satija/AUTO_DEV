const express = require('express');
const router = express.Router();
const Role = require('../models/roles');

// Get all roles
router.get('/', async (req, res) => {
  try {
    const roles = await Role.find();
    res.json(roles);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Get role by ID
router.get('/:id', async (req, res) => {
  try {
    const role = await Role.findById(req.params.id);
    if (!role) return res.status(404).json({ msg: 'Role not found' });
    res.json(role);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Role not found' });
    }
    res.status(500).send('Server error');
  }
});

// Create new role
router.post('/', async (req, res) => {
  const { name, permissions } = req.body;

  try {
    const newRole = new Role({
      name,
      permissions
    });

    const role = await newRole.save();
    res.json(role);
  } catch (err) {
    console.error(err.message);
    if (err.code === 11000) {
      return res.status(400).json({ msg: 'Role name already exists' });
    }
    res.status(500).send('Server error');
  }
});

// Update role
router.put('/:id', async (req, res) => {
  const { name, permissions } = req.body;

  try {
    let role = await Role.findById(req.params.id);
    if (!role) return res.status(404).json({ msg: 'Role not found' });

    role.name = name || role.name;
    role.permissions = permissions !== undefined ? permissions : role.permissions;

    const updatedRole = await role.save();
    res.json(updatedRole);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Role not found' });
    }
    if (err.code === 11000) {
      return res.status(400).json({ msg: 'Role name already exists' });
    }
    res.status(500).send('Server error');
  }
});

// Delete role
router.delete('/:id', async (req, res) => {
  try {
    const role = await Role.findById(req.params.id);
    if (!role) return res.status(404).json({ msg: 'Role not found' });

    await role.remove();
    res.json({ msg: 'Role removed' });
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Role not found' });
    }
    res.status(500).send('Server error');
  }
});

module.exports = router;