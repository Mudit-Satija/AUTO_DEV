const express = require('express');
const transactionModel = require('../models/transaction');
const router = express.Router();

// GET all transactions
router.get('/', async (req, res) => {
  try {
    const transactions = await transactionModel.find().sort({ date: -1 });
    res.json(transactions);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// GET transaction by ID
router.get('/:id', async (req, res) => {
  try {
    const transaction = await transactionModel.findById(req.params.id);
    if (!transaction) {
      return res.status(404).json({ message: 'Transaction not found' });
    }
    res.json(transaction);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// POST create transaction
router.post('/', async (req, res) => {
  const transaction = new transactionModel({
    amount: req.body.amount,
    description: req.body.description,
    category: req.body.category,
    date: req.body.date,
    type: req.body.type
  });

  try {
    const newTransaction = await transaction.save();
    res.status(201).json(newTransaction);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

// PUT update transaction
router.put('/:id', async (req, res) => {
  try {
    const transaction = await transactionModel.findById(req.params.id);
    if (!transaction) {
      return res.status(404).json({ message: 'Transaction not found' });
    }

    if (req.body.amount != null) transaction.amount = req.body.amount;
    if (req.body.description != null) transaction.description = req.body.description;
    if (req.body.category != null) transaction.category = req.body.category;
    if (req.body.date != null) transaction.date = req.body.date;
    if (req.body.type != null) transaction.type = req.body.type;

    const updatedTransaction = await transaction.save();
    res.json(updatedTransaction);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

// DELETE transaction
router.delete('/:id', async (req, res) => {
  try {
    const transaction = await transactionModel.findByIdAndDelete(req.params.id);
    if (!transaction) {
      return res.status(404).json({ message: 'Transaction not found' });
    }
    res.json({ message: 'Transaction deleted' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router;