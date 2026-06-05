const express = require('express');
const router = express.Router();

const workspacesRouter = require('./workspaces.js');
const projectsRouter = require('./projects.js');
const tasksRouter = require('./tasks.js');

router.use('/workspaces', workspacesRouter);
router.use('/projects', projectsRouter);
router.use('/tasks', tasksRouter);

module.exports = router;