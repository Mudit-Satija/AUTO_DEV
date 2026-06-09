const mongoose = require('mongoose');

const recordsSchema = new mongoose.Schema({
  type: {
    type: String,
    required: true,
    enum: ['create', 'update', 'delete', 'access'],
    trim: true
  },
  entity: {
    type: String,
    required: true,
    trim: true
  },
  entityId: {
    type: mongoose.Schema.Types.ObjectId,
    required: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  details: {
    type: Object,
    default: {}
  },
  ip: {
    type: String,
    trim: true
  },
  userAgent: {
    type: String,
    trim: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Record', recordsSchema);