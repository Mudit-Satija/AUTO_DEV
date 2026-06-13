const express = require('express');
const router = express.Router();

const transactionRoutes = require('./transaction');

router.use('/api/transactions', transactionRoutes);

module.exports = router;