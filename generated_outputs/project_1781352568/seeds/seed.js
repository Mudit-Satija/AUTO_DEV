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
    { name: 'Salary', color: '#FFEAA7' },
    { name: 'Freelance', color: '#DDA0DD' },
  ];

  await Category.insertMany(categories);

  const transactions = [
    {
      amount: 45.5,
      description: 'Grocery shopping',
      category: categories[0]._id,
      date: new Date('2023-10-01'),
      type: 'expense',
    },
    {
      amount: 1200,
      description: 'Monthly salary',
      category: categories[4]._id,
      date: new Date('2023-10-01'),
      type: 'income',
    },
    {
      amount: 35,
      description: 'Bus fare',
      category: categories[1]._id,
      date: new Date('2023-10-02'),
      type: 'expense',
    },
    {
      amount: 80,
      description: 'Movie tickets',
      category: categories[2]._id,
      date: new Date('2023-10-03'),
      type: 'expense',
    },
    {
      amount: 150,
      description: 'Electricity bill',
      category: categories[3]._id,
      date: new Date('2023-10-05'),
      type: 'expense',
    },
    {
      amount: 200,
      description: 'Freelance design work',
      category: categories[5]._id,
      date: new Date('2023-10-10'),
      type: 'income',
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
  ];

  await Budget.insertMany(budgets);

  console.log('Database seeded successfully');
  mongoose.connection.close();
};

seedDatabase().catch(console.error);