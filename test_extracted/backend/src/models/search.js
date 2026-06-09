const mongoose = require('mongoose');

const searchSchema = new mongoose.Schema({
  query: {
    type: String,
    required: true,
    index: 'text'
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  resultsCount: { type: Number, default: 0 },
  timestamp: { type: Date, default: Date.now },
  metadata: {
    filters: Object,
    sortBy: String,
    page: Number
  }
});

searchSchema.index({ query: 'text', 'metadata.filters': 'text' });

module.exports = mongoose.model('Search', searchSchema);