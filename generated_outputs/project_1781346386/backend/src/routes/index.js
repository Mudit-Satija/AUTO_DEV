const express = require('express');
const transactionRouter = require('./transaction');
const budgetRouter = require('./budget');
const categoryRouter = require('./category');

const router = express.Router();

router.use('/transactions', transactionRouter);
router.use('/budgets', budgetRouter);
router.use('/categories', categoryRouter);

module.exports = router;