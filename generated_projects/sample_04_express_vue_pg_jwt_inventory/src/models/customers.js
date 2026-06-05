const pool = require('../config/database');

const getAllCustomers = async () => {
  const result = await pool.query('SELECT * FROM customers ORDER BY id');
  return result.rows;
};

const getCustomerById = async (id) => {
  const result = await pool.query('SELECT * FROM customers WHERE id = $1', [id]);
  return result.rows[0];
};

const createCustomer = async (name, email, phone) => {
  const result = await pool.query(
    'INSERT INTO customers (name, email, phone) VALUES ($1, $2, $3) RETURNING *',
    [name, email, phone]
  );
  return result.rows[0];
};

const updateCustomer = async (id, name, email, phone) => {
  const result = await pool.query(
    'UPDATE customers SET name = $1, email = $2, phone = $3 WHERE id = $4 RETURNING *',
    [name, email, phone, id]
  );
  return result.rows[0];
};

const deleteCustomer = async (id) => {
  const result = await pool.query('DELETE FROM customers WHERE id = $1 RETURNING *', [id]);
  return result.rows[0];
};

module.exports = {
  getAllCustomers,
  getCustomerById,
  createCustomer,
  updateCustomer,
  deleteCustomer
};