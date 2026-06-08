const mongoose = require('mongoose');
const connectDB = require('../backend/src/config/database');
const Calculator = require('../backend/src/models/calculator');

async function seed() {
  await connectDB();

  const calculatorData = [
    { operation: 'add', operands: [5, 3], result: 8 },
    { operation: 'subtract', operands: [10, 4], result: 6 },
    { operation: 'multiply', operands: [7, 6], result: 42 },
    { operation: 'divide', operands: [15, 3], result: 5 },
    { operation: 'add', operands: [1, 1], result: 2 },
  ];

  await Calculator.deleteMany({});
  await Calculator.insertMany(calculatorData);

  console.log('Seed data inserted successfully.');

  await mongoose.connection.close();
}

seed().catch(err => {
  console.error('Error seeding data:', err);
  mongoose.connection.close();
});