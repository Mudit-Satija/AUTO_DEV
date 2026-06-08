const mongoose = require('mongoose');

const calculatorSchema = new mongoose.Schema({
  operation: {
    type: String,
    required: true,
    enum: ['add', 'subtract', 'multiply', 'divide'],
  },
  operand1: {
    type: Number,
    required: true,
  },
  operand2: {
    type: Number,
    required: true,
  },
  result: {
    type: Number,
    required: true,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model('Calculator', calculatorSchema);