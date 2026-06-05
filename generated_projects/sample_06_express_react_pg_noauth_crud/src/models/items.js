const pool = require('../config/database');

const getAllItems = async () => {
  const result = await pool.query(
    'SELECT i.id, i.name, i.description, i.category_id, c.name AS category_name FROM items i LEFT JOIN categories c ON i.category_id = c.id ORDER BY i.name'
  );
  return result.rows;
};

const getItemById = async (id) => {
  const result = await pool.query(
    'SELECT i.id, i.name, i.description, i.category_id, c.name AS category_name FROM items i LEFT JOIN categories c ON i.category_id = c.id WHERE i.id = $1',
    [id]
  );
  return result.rows[0];
};

const createItem = async (name, description, categoryId) => {
  const result = await pool.query(
    'INSERT INTO items (name, description, category_id) VALUES ($1, $2, $3) RETURNING id, name, description, category_id',
    [name, description, categoryId]
  );
  return result.rows[0];
};

const updateItem = async (id, name, description, categoryId) => {
  const result = await pool.query(
    'UPDATE items SET name = $1, description = $2, category_id = $3 WHERE id = $4 RETURNING id, name, description, category_id',
    [name, description, categoryId, id]
  );
  return result.rows[0];
};

const deleteItem = async (id) => {
  const result = await pool.query('DELETE FROM items WHERE id = $1 RETURNING id', [id]);
  return result.rows[0];
};

module.exports = {
  getAllItems,
  getItemById,
  createItem,
  updateItem,
  deleteItem,
};