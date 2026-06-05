const { Pool } = require('pg');
const config = require('../config');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  database: config.db.name,
  user: config.db.user,
  password: config.db.password
});

const getEvents = async () => {
  const result = await pool.query('SELECT * FROM events ORDER BY created_at DESC');
  return result.rows;
};

const getEventById = async (id) => {
  const result = await pool.query('SELECT * FROM events WHERE id = $1', [id]);
  return result.rows[0];
};

const createEvent = async (title, description, date, location) => {
  const result = await pool.query(
    'INSERT INTO events (title, description, date, location, created_at) VALUES ($1, $2, $3, $4, NOW()) RETURNING *',
    [title, description, date, location]
  );
  return result.rows[0];
};

const updateEvent = async (id, title, description, date, location) => {
  const result = await pool.query(
    'UPDATE events SET title = $1, description = $2, date = $3, location = $4, updated_at = NOW() WHERE id = $5 RETURNING *',
    [title, description, date, location, id]
  );
  return result.rows[0];
};

const deleteEvent = async (id) => {
  const result = await pool.query('DELETE FROM events WHERE id = $1 RETURNING *', [id]);
  return result.rows[0];
};

module.exports = {
  getEvents,
  getEventById,
  createEvent,
  updateEvent,
  deleteEvent
};