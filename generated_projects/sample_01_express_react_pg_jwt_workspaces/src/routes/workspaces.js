const express = require('express');
const router = express.Router();
const workspacesModel = require('../models/workspaces');

router.get('/', async (req, res) => {
  try {
    const workspaces = await workspacesModel.getAllWorkspaces();
    res.json(workspaces);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const workspace = await workspacesModel.getWorkspaceById(req.params.id);
    if (!workspace) {
      return res.status(404).json({ error: 'Workspace not found' });
    }
    res.json(workspace);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const { name, description } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    const workspace = await workspacesModel.createWorkspace(name, description);
    res.status(201).json(workspace);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { name, description } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    const updated = await workspacesModel.updateWorkspace(req.params.id, name, description);
    if (!updated) {
      return res.status(404).json({ error: 'Workspace not found' });
    }
    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const deleted = await workspacesModel.deleteWorkspace(req.params.id);
    if (!deleted) {
      return res.status(404).json({ error: 'Workspace not found' });
    }
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;