const express = require('express');
const router = express.Router();

const postsRoutes = require('./posts');
const inventoryRoutes = require('./inventory');

router.use('/posts', postsRoutes);
router.use('/inventory', inventoryRoutes);

module.exports = router;