const mongoose = require('mongoose');

const auditSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  action: {
    type: String,
    required: true,
    enum: ['create', 'read', 'update', 'delete'],
  },
  resource: {
    type: String,
    required: true,
  },
  resourceId: {
    type: mongoose.Schema.Types.ObjectId,
    required: true,
  },
  details: mongoose.Schema.Types.Mixed,
  ip: String,
  userAgent: String,
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model('Audit', auditSchema);