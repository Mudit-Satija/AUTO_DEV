const express = require('express');
const router = express.Router();
const Search = require('../models/search');
const authenticateToken = require('../middleware/auth');
router.use(authenticateToken)
router.get('/stats', async (req, res) => {
  const count = await Search.countDocuments();
  res.json({ count });
});
router.get('/', async (req, res) => {
  const items = await Search.find();
  res.json(items);
});
router.get('/:id', async (req, res) => {
  const item = await Search.findById(req.params.id);
  if (!item) return res.status(404).json({ message: 'Not found' });
  res.json(item);
});
router.post('/', async (req, res) => {
  const item = await Search.create(req.body);
  res.status(201).json(item);
});
router.put('/:id', async (req, res) => {
  const item = await Search.findByIdAndUpdate(req.params.id, req.body, { new: true });
  if (!item) return res.status(404).json({ message: 'Not found' });
  res.json(item);
});
router.delete('/:id', async (req, res) => {
  await Search.findByIdAndDelete(req.params.id);
  res.status(204).end();
});
module.exports = router;