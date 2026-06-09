const mongoose = require('mongoose');

const webhookSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  url: {
    type: String,
    required: true,
    match: [/^https?:\/\/.+/i, 'URL must be valid']
  },
  event: {
    type: String,
    required: true,
    enum: ['user.created', 'user.updated', 'user.deleted', 'data.changed']
  },
  isActive: { type: Boolean, default: true },
  headers: { type: Object, default: {} },
  secret: { type: String },
  lastTriggered: { type: Date },
  failureCount: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

webhookSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Webhook', webhookSchema);