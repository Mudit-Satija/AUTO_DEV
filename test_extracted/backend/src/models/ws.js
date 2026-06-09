const mongoose = require('mongoose');

const wsSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  socketId: {
    type: String,
    required: true,
    unique: true
  },
  connectedAt: {
    type: Date,
    default: Date.now
  },
  lastActive: {
    type: Date,
    default: Date.now
  },
  metadata: {
    type: Object,
    default: {}
  }
});

wsSchema.pre('save', function(next) {
  this.lastActive = Date.now();
  next();
});

module.exports = mongoose.model('WebSocket', wsSchema);