const express = require('express');
const transactionRouter = require('./transaction');

const router = express.Router();

router.use('/transactions', transactionRouter);

module.exports = router;