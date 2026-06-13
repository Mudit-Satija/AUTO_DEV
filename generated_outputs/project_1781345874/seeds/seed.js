const mongoose = require('mongoose');
const Transaction = require('../models/Transaction');
const Budget = require('../models/Budget');
const Category = require('../models/Category');

const seedDatabase = async () => {
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
    { name: 'Salary', color: '#74B9FF' },
    { name: 'Freelance', color: '#00B894' },
  ];

  await Category.insertMany(categories);

  const transactions = [
    {
      amount: 45.5,
      category: categories[0]._id,
      date: new Date('2023-10-01'),
      description: 'Grocery shopping',
      type: 'expense',
    },
    {
      amount: 1200,
      category: categories[6]._id,
      date: new Date('2023-10-01'),
      description: 'Monthly salary',
      type: 'income',
    },
    {
      amount: 35,
      category: categories[1]._id,
      date: new Date('2023-10-02'),
      description: 'Gas refill',
      type: 'expense',
    },
    {
      amount: 80,
      category: categories[2]._id,
      date: new Date('2023-10-03'),
      description: 'Movie tickets',
      type: 'expense',
    },
    {
      amount: 150,
      category: categories[3]._id,
      date: new Date('2023-10-04'),
      description: 'Electricity bill',
      type: 'expense',
    },
    {
      amount: 200,
      category: categories[7]._id,
      date: new Date('2023-10-05'),
      description: 'Freelance design project',
      type: 'income',
    },
    {
      amount: 60,
      category: categories[0]._id,
      date: new Date('2023-10-06'),
      description: 'Dinner with friends',
      type: 'expense',
    },
    {
      amount: 75,
      category: categories[4]._id,
      date: new Date('2023-10-07'),
      description: 'Pharmacy purchase',
      type: 'expense',
    },
    {
      amount: 1200,
      category: categories[6]._id,
      date: new Date('2023-09-01'),
      description: 'Previous month salary',
      type: 'income',
    },
    {
      amount: 90,
      category: categories[1]._id,
      date: new Date('2023-09-15'),
      description: 'Public transit pass',
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
      amount: 150,
      month: '2023-10',
    },
    {
      category: categories[3]._id,
      amount: 300,
      month: '2023-10',
    },
    {
      category: categories[4]._id,
      amount: 100,
      month: '2023-10',
    },
    {
      category: categories[5]._id,
      amount: 1200,
      month: '2023-10',
    },
  ];

  await Budget.insertMany(budgets);

  console.log('Database seeded successfully');
  mongoose.connection.close();
};

seedDatabase().catch(console.error);