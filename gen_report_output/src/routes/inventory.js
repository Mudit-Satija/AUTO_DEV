const express = require('express');
const router = express.Router();
const Inventory = require('../models/inventory');

// Get all inventory items
router.get('/', async (req, res) => {
  try {
    const items = await Inventory.find();
    res.json(items);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Get inventory item by ID
router.get('/:id', async (req, res) => {
  try {
    const item = await Inventory.findById(req.params.id);
    if (!item) return res.status(404).json({ msg: 'Item not found' });
    res.json(item);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Item not found' });
    }
    res.status(500).send('Server error');
  }
});

// Create new inventory item
router.post('/', async (req, res) => {
  const { name, quantity, category, location } = req.body;

  try {
    const newItem = new Inventory({
      name,
      quantity,
      category,
      location
    });

    const item = await newItem.save();
    res.json(item);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Update inventory item
router.put('/:id', async (req, res) => {
  const { name, quantity, category, location } = req.body;

  try {
    let item = await Inventory.findById(req.params.id);
    if (!item) return res.status(404).json({ msg: 'Item not found' });

    item.name = name || item.name;
    item.quantity = quantity !== undefined ? quantity : item.quantity;
    item.category = category || item.category;
    item.location = location || item.location;

    const updatedItem = await item.save();
    res.json(updatedItem);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Item not found' });
    }
    res.status(500).send('Server error');
  }
});

// Delete inventory item
router.delete('/:id', async (req, res) => {
  try {
    const item = await Inventory.findById(req.params.id);
    if (!item) return res.status(404).json({ msg: 'Item not found' });

    await item.remove();
    res.json({ msg: 'Item removed' });
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Item not found' });
    }
    res.status(500).send('Server error');
  }
});

module.exports = router;