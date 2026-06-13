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
    { name: 'Housing', color: '#FFEAA7' },
    { name: 'Healthcare', color: '#DDA0DD' },
    { name: 'Salary', color: '#74B9FF' },
    { name: 'Freelance', color: '#55EFCE' },
  ];

  const createdCategories = await Category.insertMany(categories);

  const transactions = [
    {
      amount: 45.5,
      category: createdCategories.find(c => c.name === 'Food')._id,
      date: new Date('2023-10-01'),
      description: 'Grocery shopping',
      type: 'expense',
    },
    {
      amount: 1200,
      category: createdCategories.find(c => c.name === 'Salary')._id,
      date: new Date('2023-10-01'),
      description: 'Monthly salary',
      type: 'income',
    },
    {
      amount: 80,
      category: createdCategories.find(c => c.name === 'Transportation')._id,
      date: new Date('2023-10-03'),
      description: 'Gas refill',
      type: 'expense',
    },
    {
      amount: 30,
      category: createdCategories.find(c => c.name === 'Entertainment')._id,
      date: new Date('2023-10-05'),
      description: 'Movie tickets',
      type: 'expense',
    },
    {
      amount: 200,
      category: createdCategories.find(c => c.name === 'Freelance')._id,
      date: new Date('2023-10-10'),
      description: 'Web design project',
      type: 'income',
    },
    {
      amount: 150,
      category: createdCategories.find(c => c.name === 'Housing')._id,
      date: new Date('2023-10-15'),
      description: 'Rent payment',
      type: 'expense',
    },
    {
      amount: 45,
      category: createdCategories.find(c => c.name === 'Utilities')._id,
      date: new Date('2023-10-18'),
      description: 'Electricity bill',
      type: 'expense',
    },
    {
      amount: 60,
      category: createdCategories.find(c => c.name === 'Healthcare')._id,
      date: new Date('2023-10-20'),
      description: 'Pharmacy',
      type: 'expense',
    },
  ];

  await Transaction.insertMany(transactions);

  const budgets = [
    {
      category: createdCategories.find(c => c.name === 'Food')._id,
      amount: 500,
      month: '2023-10',
    },
    {
      category: createdCategories.find(c => c.name === 'Transportation')._id,
      amount: 200,
      month: '2023-10',
    },
    {
      category: createdCategories.find(c => c.name === 'Entertainment')._id,
      amount: 100,
      month: '2023-10',
    },
    {
      category: createdCategories.find(c => c.name === 'Utilities')._id,
      amount: 150,
      month: '2023-10',
    },
    {
      category: createdCategories.find(c => c.name === 'Housing')._id,
      amount: 1200,
      month: '2023-10',
    },
    {
      category: createdCategories.find(c => c.name === 'Healthcare')._id,
      amount: 100,
      month: '2023-10',
    },
  ];

  await Budget.insertMany(budgets);

  console.log('Database seeded successfully');
  mongoose.connection.close();
};

seedDatabase().catch(console.error);