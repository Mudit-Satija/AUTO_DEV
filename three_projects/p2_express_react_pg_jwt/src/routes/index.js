const express = require('express');
const usersRouter = require('./users');
const ordersRouter = require('./orders');
const productsRouter = require('./products');

const router = express.Router();

router.use('/users', usersRouter);
router.use('/orders', ordersRouter);
router.use('/products', productsRouter);

module.exports = router;