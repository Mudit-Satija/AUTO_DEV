const express = require('express');
const productRoutes = require('./products');
const orderRoutes = require('./orders');

const router = express.Router();

router.use('/products', productRoutes);
router.use('/orders', orderRoutes);

module.exports = router;