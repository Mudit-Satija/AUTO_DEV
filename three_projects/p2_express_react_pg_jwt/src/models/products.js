const pool = require('../config/database');

const createProduct = async (name, description, price, stock, userId) => {
  const query = `
    INSERT INTO products (name, description, price, stock, created_by)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING *;
  `;
  const values = [name, description, price, stock, userId];
  const result = await pool.query(query, values);
  return result.rows[0];
};

const getProductById = async (id) => {
  const query = `
    SELECT * FROM products WHERE id = $1 AND deleted_at IS NULL;
  `;
  const result = await pool.query(query, [id]);
  return result.rows[0];
};

const getAllProducts = async () => {
  const query = `
    SELECT * FROM products WHERE deleted_at IS NULL ORDER BY created_at DESC;
  `;
  const result = await pool.query(query);
  return result.rows;
};

const updateProduct = async (id, name, description, price, stock, userId) => {
  const query = `
    UPDATE products
    SET name = $1, description = $2, price = $3, stock = $4, updated_by = $5, updated_at = NOW()
    WHERE id = $6 AND deleted_at IS NULL
    RETURNING *;
  `;
  const values = [name, description, price, stock, userId, id];
  const result = await pool.query(query, values);
  return result.rows[0];
};

const deleteProduct = async (id, userId) => {
  const query = `
    UPDATE products
    SET deleted_at = NOW(), deleted_by = $1
    WHERE id = $2 AND deleted_at IS NULL
    RETURNING *;
  `;
  const result = await pool.query(query, [userId, id]);
  return result.rows[0];
};

module.exports = {
  createProduct,
  getProductById,
  getAllProducts,
  updateProduct,
  deleteProduct
};