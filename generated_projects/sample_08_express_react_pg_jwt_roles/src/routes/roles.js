const express = require('express');
const router = express.Router();
const pool = require('../config/database');

router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT r.id, r.name, r.created_at, ARRAY_AGG(p.name) AS permissions FROM roles r LEFT JOIN role_permissions rp ON r.id = rp.role_id LEFT JOIN permissions p ON rp.permission_id = p.id GROUP BY r.id, r.name, r.created_at ORDER BY r.name');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('SELECT r.id, r.name, r.created_at, ARRAY_AGG(p.name) AS permissions FROM roles r LEFT JOIN role_permissions rp ON r.id = rp.role_id LEFT JOIN permissions p ON rp.permission_id = p.id WHERE r.id = $1 GROUP BY r.id, r.name, r.created_at', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Role not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/', async (req, res) => {
  try {
    const { name, permission_ids } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    const result = await pool.query('INSERT INTO roles (name) VALUES ($1) RETURNING id, name, created_at', [name]);
    const roleId = result.rows[0].id;

    if (permission_ids && Array.isArray(permission_ids)) {
      const permissionValues = permission_ids.map(pid => `(${roleId}, ${pid})`).join(',');
      if (permissionValues) {
        await pool.query(`INSERT INTO role_permissions (role_id, permission_id) VALUES ${permissionValues}`);
      }
    }

    res.status(201).json(result.rows[0]);
  } catch (err) {
    if (err.code === '23505') {
      return res.status(409).json({ error: 'Role name already exists' });
    }
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { name, permission_ids } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }

    const updateResult = await pool.query('UPDATE roles SET name = $1 WHERE id = $2 RETURNING id, name, created_at', [name, id]);
    if (updateResult.rows.length === 0) {
      return res.status(404).json({ error: 'Role not found' });
    }

    await pool.query('DELETE FROM role_permissions WHERE role_id = $1', [id]);
    if (permission_ids && Array.isArray(permission_ids)) {
      const permissionValues = permission_ids.map(pid => `(${id}, ${pid})`).join(',');
      if (permissionValues) {
        await pool.query(`INSERT INTO role_permissions (role_id, permission_id) VALUES ${permissionValues}`);
      }
    }

    res.json(updateResult.rows[0]);
  } catch (err) {
    if (err.code === '23505') {
      return res.status(409).json({ error: 'Role name already exists' });
    }
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('DELETE FROM roles WHERE id = $1 RETURNING id', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Role not found' });
    }
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;