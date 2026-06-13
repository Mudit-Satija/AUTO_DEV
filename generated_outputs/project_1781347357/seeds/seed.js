const mongoose = require('mongoose');
const Transaction = require('../models/Transaction');
const Budget = require('../models/Budget');
const Category = require('../models/Category');

const seedData = async () => {
  await mongoose.connect('mongodb://localhost:27017/expenseflow', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  });

  await Transaction.deleteMany({});
  await Budget.deleteMany({});
  await Category.deleteMany({});

  const categories = [
    { name: 'Food', color: '#FF6B6B' },
    { name: 'Transportation', color: '#4ECDC4' },
    { name: 'Entertainment', color: '#45B7D1' },
    { name: 'Utilities', color: '#96CEB4' },
    { name: 'Healthcare', color: '#FFEAA7' },
    { name: 'Housing', color: '#DDA0DD' },
    { name: 'Salary', color: '#778BE3' },
    { name: 'Other', color: '#A0A0A0' },
  ];

  await Category.insertMany(categories);

  const transactions = [
    {
      amount: 45.5,
      category: categories[0]._id,
      description: 'Grocery shopping',
      date: new Date('2023-10-01'),
      type: 'expense',
    },
    {
      amount: 1200,
      category: categories[6]._id,
      description: 'Monthly salary',
      date: new Date('2023-10-01'),
      type: 'income',
    },
    {
      amount: 80,
      category: categories[1]._id,
      description: 'Gas refill',
      date: new Date('2023-10-05'),
      type: 'expense',
    },
    {
      amount: 30,
      category: categories[2]._id,
      description: 'Movie tickets',
      date: new Date('2023-10-07'),
      type: 'expense',
    },
    {
      amount: 150,
      category: categories[3]._id,
      description: 'Electricity bill',
      date: new Date('2023-10-10'),
      type: 'expense',
    },
    {
      amount: 200,
      category: categories[4]._id,
      description: 'Prescription',
      date: new Date('2023-10-15'),
      type: 'expense',
    },
    {
      amount: 1200,
      category: categories[5]._id,
      description: 'Rent',
      date: new Date('2023-10-01'),
      type: 'expense',
    },
    {
      amount: 25,
      category: categories[7]._id,
      description: 'Coffee with friend',
      date: new Date('2023-10-20'),
      type: 'expense',
    },
  ];

  await Transaction.insertMany(transactions);

  const budgets = [
    {
      category: categories[0]._id,
      amount: 500,
      month: '2023-10',
    },
    {
      category: categories[1]._id,
      amount: 200,
      month: '2023-10',
    },
    {
      category: categories[2]._id,
      amount: 100,
      month: '2023-10',
    },
    {
      category: categories[3]._id,
      amount: 250,
      month: '2023-10',
    },
    {
      category: categories[4]._id,
      amount: 150,
      month: '2023-10',
    },
    {
      category: categories[5]._id,
      amount: 1200,
      month: '2023-10',
    },
  ];

  await Budget.insertMany(budgets);

  console.log('Seed data inserted successfully');
  process.exit();
};

seedData().catch(err => {
  console.error('Error seeding data:', err);
  process.exit(1);
});