const express = require('express');
const router = express.Router();

const authRoutes = require('./auth');
const workspacesRoutes = require('./workspaces');
const projectsRoutes = require('./projects');
const tasksRoutes = require('./tasks');

router.use('/auth', authRoutes);
router.use('/workspaces', workspacesRoutes);
router.use('/projects', projectsRoutes);
router.use('/tasks', tasksRoutes);

module.exports = router;