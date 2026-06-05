const express = require('express');
const pool = require('../config/db');

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT t.*, p.name AS project_name FROM tasks t JOIN projects p ON t.project_id = p.id WHERE p.user_id = $1',
      [req.user.id]
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error fetching tasks.' });
  }
});

router.get('/project/:projectId', async (req, res) => {
  const { projectId } = req.params;

  try {
    const projectResult = await pool.query(
      'SELECT id FROM projects WHERE id = $1 AND user_id = $2',
      [projectId, req.user.id]
    );

    if (projectResult.rows.length === 0) {
      return res.status(404).json({ message: 'Project not found or not authorized.' });
    }

    const result = await pool.query(
      'SELECT * FROM tasks WHERE project_id = $1',
      [projectId]
    );

    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error fetching tasks.' });
  }
});

router.post('/', async (req, res) => {
  const { title, description, status, project_id } = req.body;

  if (!title || !project_id) {
    return res.status(400).json({ message: 'Title and project_id are required.' });
  }

  try {
    const projectResult = await pool.query(
      'SELECT id FROM projects WHERE id = $1 AND user_id = $2',
      [project_id, req.user.id]
    );

    if (projectResult.rows.length === 0) {
      return res.status(404).json({ message: 'Project not found or not authorized.' });
    }

    const result = await pool.query(
      'INSERT INTO tasks (title, description, status, project_id) VALUES ($1, $2, $3, $4) RETURNING *',
      [title, description, status || 'todo', project_id]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error creating task.' });
  }
});

router.put('/:id', async (req, res) => {
  const { id } = req.params;
  const { title, description, status, project_id } = req.body;

  if (!title) {
    return res.status(400).json({ message: 'Task title is required.' });
  }

  try {
    const taskResult = await pool.query(
      'SELECT t.project_id FROM tasks t JOIN projects p ON t.project_id = p.id WHERE t.id = $1 AND p.user_id = $2',
      [id, req.user.id]
    );

    if (taskResult.rows.length === 0) {
      return res.status(404).json({ message: 'Task not found or not authorized.' });
    }

    const projectResult = project_id
      ? await pool.query(
          'SELECT id FROM projects WHERE id = $1 AND user_id = $2',
          [project_id, req.user.id]
        )
      : { rows: [{ id: taskResult.rows[0].project_id }] };

    if (project_id && projectResult.rows.length === 0) {
      return res.status(404).json({ message: 'Project not found or not authorized.' });
    }

    const result = await pool.query(
      'UPDATE tasks SET title = $1, description = $2, status = $3, project_id = $4 WHERE id = $5 RETURNING *',
      [title, description, status, project_id || taskResult.rows[0].project_id, id]
    );

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error updating task.' });
  }
});

router.delete('/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query(
      'DELETE FROM tasks t USING projects p WHERE t.id = $1 AND t.project_id = p.id AND p.user_id = $2 RETURNING *',
      [id, req.user.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Task not found or not authorized.' });
    }

    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error deleting task.' });
  }
});

module.exports = router;