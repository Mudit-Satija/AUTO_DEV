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
    { name: 'Rent', color: '#FFEAA7' },
    { name: 'Salary', color: '#DDA0DD' },
    { name: 'Healthcare', color: '#F7DC6F' },
    { name: 'Education', color: '#BB8FCE' },
  ];

  const createdCategories = await Category.insertMany(categories);

  const budgets = [
    {
      category: createdCategories.find(c => c.name === 'Food')?._id,
      amount: 500,
      month: '2023-10',
      spent: 320,
    },
    {
      category: createdCategories.find(c => c.name === 'Transportation')?._id,
      amount: 200,
      month: '2023-10',
      spent: 180,
    },
    {
      category: createdCategories.find(c => c.name === 'Entertainment')?._id,
      amount: 150,
      month: '2023-10',
      spent: 120,
    },
    {
      category: createdCategories.find(c => c.name === 'Utilities')?._id,
      amount: 300,
      month: '2023-10',
      spent: 290,
    },
    {
      category: createdCategories.find(c => c.name === 'Rent')?._id,
      amount: 1200,
      month: '2023-10',
      spent: 1200,
    },
  ];

  const createdBudgets = await Budget.insertMany(budgets);

  const transactions = [
    {
      amount: 45,
      category: createdCategories.find(c => c.name === 'Food')?._id,
      date: new Date('2023-10-01'),
      description: 'Grocery shopping',
      type: 'expense',
    },
    {
      amount: 120,
      category: createdCategories.find(c => c.name === 'Transportation')?._id,
      date: new Date('2023-10-02'),
      description: 'Gas refill',
      type: 'expense',
    },
    {
      amount: 80,
      category: createdCategories.find(c => c.name === 'Entertainment')?._id,
      date: new Date('2023-10-03'),
      description: 'Movie tickets',
      type: 'expense',
    },
    {
      amount: 150,
      category: createdCategories.find(c => c.name === 'Utilities')?._id,
      date: new Date('2023-10-04'),
      description: 'Electricity bill',
      type: 'expense',
    },
    {
      amount: 1200,
      category: createdCategories.find(c => c.name === 'Salary')?._id,
      date: new Date('2023-10-05'),
      description: 'Monthly salary',
      type: 'income',
    },
    {
      amount: 30,
      category: createdCategories.find(c => c.name === 'Food')?._id,
      date: new Date('2023-10-06'),
      description: 'Dinner out',
      type: 'expense',
    },
    {
      amount: 40,
      category: createdCategories.find(c => c.name === 'Transportation')?._id,
      date: new Date('2023-10-07'),
      description: 'Bus fare',
      type: 'expense',
    },
    {
      amount: 50,
      category: createdCategories.find(c => c.name === 'Entertainment')?._id,
      date: new Date('2023-10-08'),
      description: 'Concert tickets',
      type: 'expense',
    },
    {
      amount: 75,
      category: createdCategories.find(c => c.name === 'Healthcare')?._id,
      date: new Date('2023-10-09'),
      description: 'Pharmacy',
      type: 'expense',
    },
    {
      amount: 200,
      category: createdCategories.find(c => c.name === 'Education')?._id,
      date: new Date('2023-10-10'),
      description: 'Online course',
      type: 'expense',
    },
  ];

  await Transaction.insertMany(transactions);

  console.log('Seed data inserted successfully');
  mongoose.connection.close();
};

seedData().catch(console.error);