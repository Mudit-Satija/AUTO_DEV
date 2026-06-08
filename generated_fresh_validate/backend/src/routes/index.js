const express = require('express');
const router = express.Router();

const tasksRouter = require('./tasks.js');
const categoriesRouter = require('./categories.js');
const usersRouter = require('./users.js');

router.use('/tasks', tasksRouter);
router.use('/categories', categoriesRouter);
router.use('/users', usersRouter);

module.exports = router;