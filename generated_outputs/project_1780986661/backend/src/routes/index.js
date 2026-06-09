const express = require('express');
const router = express.Router();

const dashboard = require('./dashboard');
const createTask = require('./createTask');
const taskDetails = require('./taskDetails');
const completedTasks = require('./completedTasks');

router.use('/dashboard', dashboard);
router.use('/create-task', createTask);
router.use('/task-details', taskDetails);
router.use('/completed-tasks', completedTasks);

module.exports = router;