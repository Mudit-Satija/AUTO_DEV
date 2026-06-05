const express = require('express');
const authRoutes = require('./auth');
const userRoutes = require('./user');
const productRoutes = require('./product');

const router = express.Router();

router.use('/auth', authRoutes);
router.use('/users', userRoutes);
router.use('/products', productRoutes);

module.exports = router;