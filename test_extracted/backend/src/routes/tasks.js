const express = require('express');
const router = express.Router();
const Task = require('../models/tasks');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);

router.get('/stats', async (req, res) => {
  const count = await Task.countDocuments();
  res.json({ count });
});

router.get('/', async (req, res) => {
  const items = await Task.find();
  res.json(items);
});

router.get('/:id', async (req, res) => {
  const item = await Task.findById(req.params.id);
  if (!item) return res.status(404).json({ message: 'Not found' });
  res.json(item);
});

router.post('/', async (req, res) => {
  const item = await Task.create(req.body);
  res.status(201).json(item);
});

router.put('/:id', async (req, res) => {
  const item = await Task.findByIdAndUpdate(req.params.id, req.body, { new: true });
  if (!item) return res.status(404).json({ message: 'Not found' });
  res.json(item);
});

router.delete('/:id', async (req, res) => {
  await Task.findByIdAndDelete(req.params.id);
  res.status(204).end();
});

module.exports = router;