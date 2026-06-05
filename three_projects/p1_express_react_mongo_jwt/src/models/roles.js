const mongoose = require('mongoose');

const roleSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true,
    enum: ['admin', 'editor', 'viewer'],
    lowercase: true
  },
  permissions: [{
    type: String,
    enum: ['read', 'write', 'delete', 'manage_users']
  }],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Role', roleSchema);