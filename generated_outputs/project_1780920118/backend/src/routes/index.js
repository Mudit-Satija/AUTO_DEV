const express = require('express');
const router = express.Router();

const tasksRoutes = require('./tasks');

router.use('/tasks', tasksRoutes);

module.exports = router;