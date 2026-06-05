const express = require('express');
const router = express.Router();

const userRoutes = require('./user');
const productRoutes = require('./product');

router.use('/users', userRoutes);
router.use('/products', productRoutes);

module.exports = router;