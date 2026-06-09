const mongoose = require('mongoose');

const settingsSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  theme: { type: String, enum: ['light', 'dark', 'system'], default: 'light' },
  language: { type: String, default: 'en' },
  notifications: {
    email: { type: Boolean, default: true },
    inApp: { type: Boolean, default: true },
    push: { type: Boolean, default: false }
  },
  privacy: {
    publicProfile: { type: Boolean, default: false },
    shareData: { type: Boolean, default: true }
  },
  updatedAt: { type: Date, default: Date.now }
});

settingsSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Settings', settingsSchema);