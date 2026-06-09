const mongoose = require('mongoose');

const dashboardSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  data: {
    type: Object,
    required: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

dashboardSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Dashboard', dashboardSchema);