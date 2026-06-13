const express = require('express');
const router = express.Router();
const Budget = require('../models/budget');

router.get('/', async (req, res) => {
  try {
    const budgets = await Budget.find().populate('category', 'name');
    res.json(budgets);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const budget = await Budget.findById(req.params.id).populate('category', 'name');
    if (!budget) return res.status(404).json({ message: 'Budget not found' });
    res.json(budget);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const budget = new Budget(req.body);
    const savedBudget = await budget.save();
    res.status(201).json(savedBudget);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const budget = await Budget.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true });
    if (!budget) return res.status(404).json({ message: 'Budget not found' });
    res.json(budget);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const budget = await Budget.findByIdAndDelete(req.params.id);
    if (!budget) return res.status(404).json({ message: 'Budget not found' });
    res.json({ message: 'Budget deleted' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

router.get('/:id/transactions', async (req, res) => {
  try {
    const budget = await Budget.findById(req.params.id);
    if (!budget) return res.status(404).json({ message: 'Budget not found' });
    const transactions = await Transaction.find({ budget: budget._id }).populate('category', 'name');
    res.json(transactions);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

router.get('/summary', async (req, res) => {
  try {
    const budgets = await Budget.find().populate('category', 'name');
    const totalBudgeted = budgets.reduce((sum, b) => sum + b.amount, 0);
    const totalSpent = await Transaction.aggregate([
      { $match: { budget: { $in: budgets.map(b => b._id) } } },
      { $group: { _id: null, total: { $sum: '$amount' } } }
    ]);
    const totalSpentAmount = totalSpent.length > 0 ? totalSpent[0].total : 0;
    const remaining = totalBudgeted - totalSpentAmount;
    res.json({ totalBudgeted, totalSpent: totalSpentAmount, remaining });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router;