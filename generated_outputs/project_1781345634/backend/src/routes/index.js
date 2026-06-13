const express = require('express');
const productRoutes = require('./product');
const orderRoutes = require('./order');

const router = express.Router();

router.use('/products', productRoutes);
router.use('/orders', orderRoutes);

module.exports = router;