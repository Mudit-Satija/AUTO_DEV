const express = require('express');
const router = express.Router();

const tasksRoutes = require('./tasks.js');
const categoriesRoutes = require('./categories.js');

router.use('/tasks', tasksRoutes);
router.use('/categories', categoriesRoutes);

module.exports = router;