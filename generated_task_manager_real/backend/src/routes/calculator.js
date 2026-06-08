const express = require('express');
const router = express.Router();
const Calculator = require('../models/calculator');

router.get('/stats', async (req, res) => {
  const count = await Calculator.countDocuments();
  res.json({ count });
});

router.get('/', async (req, res) => {
  const items = await Calculator.find();
  res.json(items);
});

router.get('/:id', async (req, res) => {
  const item = await Calculator.findById(req.params.id);
  if (!item) return res.status(404).json({ message: 'Not found' });
  res.json(item);
});

router.post('/', async (req, res) => {
  const item = await Calculator.create(req.body);
  res.status(201).json(item);
});

router.put('/:id', async (req, res) => {
  const item = await Calculator.findByIdAndUpdate(
    req.params.id,
    req.body,
    { new: true }
  );
  if (!item) return res.status(404).json({ message: 'Not found' });
  res.json(item);
});

router.delete('/:id', async (req, res) => {
  await Calculator.findByIdAndDelete(req.params.id);
  res.status(204).end();
});

router.post('/evaluate', async (req, res) => {
  try {
    const { expression } = req.body;
    const result = eval(expression);
    res.json({ result });
  } catch (err) {
    res.status(400).json({ error: 'Invalid expression' });
  }
});

module.exports = router;