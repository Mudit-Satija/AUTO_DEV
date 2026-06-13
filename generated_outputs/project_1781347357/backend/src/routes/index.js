const express = require('express');
const transactionRoutes = require('./transaction');

const router = express.Router();

router.use('/transactions', transactionRoutes);

module.exports = router;