const pool = require('../config/database');

const createOrder = async (userId, productId, quantity, totalAmount) => {
  const query = `
    INSERT INTO orders (user_id, product_id, quantity, total_amount, status)
    VALUES ($1, $2, $3, $4, 'pending')
    RETURNING *;
  `;
  const values = [userId, productId, quantity, totalAmount];
  const result = await pool.query(query, values);
  return result.rows[0];
};

const getOrdersByUserId = async (userId) => {
  const query = `
    SELECT o.id, o.user_id, o.product_id, o.quantity, o.total_amount, o.status, o.created_at,
           p.name AS product_name, p.price AS product_price
    FROM orders o
    JOIN products p ON o.product_id = p.id
    WHERE o.user_id = $1
    ORDER BY o.created_at DESC;
  `;
  const result = await pool.query(query, [userId]);
  return result.rows;
};

const getOrderById = async (id) => {
  const query = `
    SELECT o.id, o.user_id, o.product_id, o.quantity, o.total_amount, o.status, o.created_at,
           p.name AS product_name, p.price AS product_price
    FROM orders o
    JOIN products p ON o.product_id = p.id
    WHERE o.id = $1;
  `;
  const result = await pool.query(query, [id]);
  return result.rows[0];
};

const updateOrderStatus = async (id, status) => {
  const query = `
    UPDATE orders
    SET status = $1, updated_at = NOW()
    WHERE id = $2
    RETURNING *;
  `;
  const values = [status, id];
  const result = await pool.query(query, values);
  return result.rows[0];
};

const getAllOrders = async () => {
  const query = `
    SELECT o.id, o.user_id, o.product_id, o.quantity, o.total_amount, o.status, o.created_at,
           u.username AS user_username, p.name AS product_name, p.price AS product_price
    FROM orders o
    JOIN users u ON o.user_id = u.id
    JOIN products p ON o.product_id = p.id
    ORDER BY o.created_at DESC;
  `;
  const result = await pool.query(query);
  return result.rows;
};

module.exports = {
  createOrder,
  getOrdersByUserId,
  getOrderById,
  updateOrderStatus,
  getAllOrders
};