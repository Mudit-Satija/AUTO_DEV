const pool = require('../config/database');

const getAllOrders = async () => {
  const result = await pool.query('SELECT * FROM orders ORDER BY id');
  return result.rows;
};

const getOrderById = async (id) => {
  const result = await pool.query('SELECT * FROM orders WHERE id = $1', [id]);
  return result.rows[0];
};

const createOrder = async (customerId, totalAmount, status) => {
  const result = await pool.query(
    'INSERT INTO orders (customer_id, total_amount, status) VALUES ($1, $2, $3) RETURNING *',
    [customerId, totalAmount, status]
  );
  return result.rows[0];
};

const updateOrder = async (id, customerId, totalAmount, status) => {
  const result = await pool.query(
    'UPDATE orders SET customer_id = $1, total_amount = $2, status = $3 WHERE id = $4 RETURNING *',
    [customerId, totalAmount, status, id]
  );
  return result.rows[0];
};

const deleteOrder = async (id) => {
  const result = await pool.query('DELETE FROM orders WHERE id = $1 RETURNING *', [id]);
  return result.rows[0];
};

module.exports = {
  getAllOrders,
  getOrderById,
  createOrder,
  updateOrder,
  deleteOrder
};