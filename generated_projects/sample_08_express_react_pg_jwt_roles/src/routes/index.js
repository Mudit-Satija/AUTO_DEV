const express = require('express');
const router = express.Router();

const workspacesRouter = require('./workspaces');
const projectsRouter = require('./projects');
const tasksRouter = require('./tasks');

router.use('/workspaces', workspacesRouter);
router.use('/projects', projectsRouter);
router.use('/tasks', tasksRouter);

module.exports = router;