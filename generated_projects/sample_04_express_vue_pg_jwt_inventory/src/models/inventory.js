const pool = require('../config/database');

const getAllInventory = async () => {
  const result = await pool.query('SELECT * FROM inventory ORDER BY id');
  return result.rows;
};

const getInventoryById = async (id) => {
  const result = await pool.query('SELECT * FROM inventory WHERE id = $1', [id]);
  return result.rows[0];
};

const createInventoryItem = async (name, quantity, price) => {
  const result = await pool.query(
    'INSERT INTO inventory (name, quantity, price) VALUES ($1, $2, $3) RETURNING *',
    [name, quantity, price]
  );
  return result.rows[0];
};

const updateInventoryItem = async (id, name, quantity, price) => {
  const result = await pool.query(
    'UPDATE inventory SET name = $1, quantity = $2, price = $3 WHERE id = $4 RETURNING *',
    [name, quantity, price, id]
  );
  return result.rows[0];
};

const deleteInventoryItem = async (id) => {
  const result = await pool.query('DELETE FROM inventory WHERE id = $1 RETURNING *', [id]);
  return result.rows[0];
};

module.exports = {
  getAllInventory,
  getInventoryById,
  createInventoryItem,
  updateInventoryItem,
  deleteInventoryItem
};