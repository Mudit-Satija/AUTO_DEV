const { Pool } = require('pg');
const config = require('../config');

const pool = new Pool({
  host: config.db.host,
  port: config.db.port,
  database: config.db.name,
  user: config.db.user,
  password: config.db.password
});

const getRegistrationsByEventId = async (eventId) => {
  const result = await pool.query(
    'SELECT r.*, u.email FROM registrations r JOIN users u ON r.user_id = u.id WHERE r.event_id = $1 ORDER BY r.registered_at DESC',
    [eventId]
  );
  return result.rows;
};

const getRegistrationByUserAndEvent = async (userId, eventId) => {
  const result = await pool.query(
    'SELECT * FROM registrations WHERE user_id = $1 AND event_id = $2',
    [userId, eventId]
  );
  return result.rows[0];
};

const registerForEvent = async (userId, eventId) => {
  const result = await pool.query(
    'INSERT INTO registrations (user_id, event_id, registered_at) VALUES ($1, $2, NOW()) RETURNING *',
    [userId, eventId]
  );
  return result.rows[0];
};

const unregisterFromEvent = async (userId, eventId) => {
  const result = await pool.query(
    'DELETE FROM registrations WHERE user_id = $1 AND event_id = $2 RETURNING *',
    [userId, eventId]
  );
  return result.rows[0];
};

module.exports = {
  getRegistrationsByEventId,
  getRegistrationByUserAndEvent,
  registerForEvent,
  unregisterFromEvent
};