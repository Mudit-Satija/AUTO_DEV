const express = require('express');
const router = express.Router();

const pendingTasksRouter = require('./pendingTasks');
const completedTasksRouter = require('./completedTasks');

router.use('/pendingTasks', pendingTasksRouter);
router.use('/completedTasks', completedTasksRouter);

module.exports = router;