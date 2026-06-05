const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

class User {
  static async findByUsername(username) {
    const result = await pool.query('SELECT * FROM users WHERE username = $1', [username]);
    return result.rows[0];
  }

  static async findByEmail(email) {
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    return result.rows[0];
  }

  static async create(username, email, passwordHash) {
    const result = await pool.query(
      'INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3) RETURNING *',
      [username, email, passwordHash]
    );
    return result.rows[0];
  }

  static async update(id, username, email) {
    const result = await pool.query(
      'UPDATE users SET username = $1, email = $2, updated_at = CURRENT_TIMESTAMP WHERE id = $3 RETURNING *',
      [username, email, id]
    );
    return result.rows[0];
  }
}

module.exports = User;