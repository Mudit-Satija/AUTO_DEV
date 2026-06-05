const express = require('express');
const router = express.Router();
const Task = require('../models/tasks.js');

// Get all tasks for user
router.get('/', async (req, res) => {
  try {
    const tasks = await Task.find({ userId: req.user.id }).sort({ createdAt: -1 });
    res.json(tasks);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Create a new task
router.post('/', async (req, res) => {
  const { title, description, completed } = req.body;

  try {
    const newTask = new Task({
      title,
      description,
      completed: completed || false,
      userId: req.user.id
    });

    const task = await newTask.save();
    res.json(task);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Update a task
router.put('/:id', async (req, res) => {
  const { title, description, completed } = req.body;

  try {
    let task = await Task.findById(req.params.id);

    if (!task) return res.status(404).json({ msg: 'Task not found' });

    if (task.userId.toString() !== req.user.id.toString()) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    task.title = title || task.title;
    task.description = description || task.description;
    task.completed = completed !== undefined ? completed : task.completed;

    task = await task.save();
    res.json(task);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Delete a task
router.delete('/:id', async (req, res) => {
  try {
    let task = await Task.findById(req.params.id);

    if (!task) return res.status(404).json({ msg: 'Task not found' });

    if (task.userId.toString() !== req.user.id.toString()) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    await task.remove();
    res.json({ msg: 'Task removed' });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

module.exports = router;