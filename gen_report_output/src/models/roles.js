const mongoose = require('mongoose');

const roleSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true,
    enum: ['admin', 'moderator', 'user']
  },
  permissions: [{
    type: String,
    enum: ['read', 'write', 'delete', 'manage_users', 'manage_roles']
  }],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Role', roleSchema);