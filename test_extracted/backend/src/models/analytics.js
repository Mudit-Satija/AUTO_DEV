const mongoose = require('mongoose');

const analyticsSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  eventType: {
    type: String,
    required: true,
    enum: ['page_view', 'click', 'form_submit', 'login', 'logout'],
  },
  metadata: {
    page: String,
    element: String,
    duration: Number,
    extra: mongoose.Schema.Types.Mixed,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model('Analytics', analyticsSchema);