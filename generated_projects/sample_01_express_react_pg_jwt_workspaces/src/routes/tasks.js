const express = require('express');
const router = express.Router();
const tasksModel = require('../models/tasks');

router.get('/', async (req, res) => {
  try {
    const tasks = await tasksModel.getAllTasks();
    res.json(tasks);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const task = await tasksModel.getTaskById(req.params.id);
    if (!task) return res.status(404).json({ error: 'Task not found' });
    res.json(task);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const { title, description, projectId, status, priority, dueDate } = req.body;
    const task = await tasksModel.createTask(title, description, projectId, status, priority, dueDate);
    res.status(201).json(task);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { title, description, projectId, status, priority, dueDate } = req.body;
    const task = await tasksModel.updateTask(req.params.id, title, description, projectId, status, priority, dueDate);
    if (!task) return res.status(404).json({ error: 'Task not found' });
    res.json(task);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const result = await tasksModel.deleteTask(req.params.id);
    if (!result) return res.status(404).json({ error: 'Task not found' });
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;