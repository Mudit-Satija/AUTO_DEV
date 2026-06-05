const jwt = require('jsonwebtoken');
const db = require('../config/database.js');

const authMiddleware = async (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Access token required' });
  }

  const token = authHeader.substring(7);

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const userResult = await db.query('SELECT id, email FROM users WHERE id = $1', [decoded.userId]);
    
    if (userResult.rows.length === 0) {
      return res.status(401).json({ message: 'User not found' });
    }

    req.user = userResult.rows[0];
    next();
  } catch (error) {
    return res.status(401).json({ message: 'Invalid or expired token' });
  }
};

module.exports = authMiddleware;