const express = require('express');
const router = express.Router();
const projectsModel = require('../models/projects');

router.get('/', async (req, res) => {
  try {
    const projects = await projectsModel.getAllByUserId(req.user.id);
    res.json(projects);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch projects' });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const project = await projectsModel.getById(req.params.id, req.user.id);
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    res.json(project);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch project' });
  }
});

router.post('/', async (req, res) => {
  try {
    const { name, workspaceId, description } = req.body;
    const project = await projectsModel.create(name, workspaceId, description, req.user.id);
    res.status(201).json(project);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create project' });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { name, workspaceId, description } = req.body;
    const project = await projectsModel.update(req.params.id, name, workspaceId, description, req.user.id);
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    res.json(project);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update project' });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const result = await projectsModel.delete(req.params.id, req.user.id);
    if (!result) {
      return res.status(404).json({ error: 'Project not found' });
    }
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete project' });
  }
});

module.exports = router;