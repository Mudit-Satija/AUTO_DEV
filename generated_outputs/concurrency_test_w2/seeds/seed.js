const mongoose = require('mongoose');
const Transaction = require('../models/Transaction');
const Budget = require('../models/Budget');
const Category = require('../models/Category');

const seedData = async () => {
  try {
    // Connect to MongoDB
    await mongoose.connect('mongodb://localhost:27017/expenseflow', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    // Clear existing data
    await Transaction.deleteMany({});
    await Budget.deleteMany({});
    await Category.deleteMany({});

    // Seed Categories
    const categories = [
      { name: 'Food', color: '#FF6B6B' },
      { name: 'Transportation', color: '#4ECDC4' },
      { name: 'Entertainment', color: '#FFD93D' },
      { name: 'Utilities', color: '#45B7D1' },
      { name: 'Healthcare', color: '#96CEB4' },
      { name: 'Rent', color: '#FEA47F' },
      { name: 'Salary', color: '#6C5CE7' },
      { name: 'Freelance', color: '#A29BFE' },
    ];

    const createdCategories = await Category.insertMany(categories);

    // Seed Budgets
    const budgets = [
      {
        category: createdCategories.find(cat => cat.name === 'Food')._id,
        amount: 500,
        month: '2023-10',
        spent: 320,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Transportation')._id,
        amount: 200,
        month: '2023-10',
        spent: 180,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Entertainment')._id,
        amount: 150,
        month: '2023-10',
        spent: 90,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Utilities')._id,
        amount: 300,
        month: '2023-10',
        spent: 280,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Rent')._id,
        amount: 1200,
        month: '2023-10',
        spent: 1200,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Salary')._id,
        amount: 3500,
        month: '2023-10',
        spent: 3500,
      },
    ];

    await Budget.insertMany(budgets);

    // Seed Transactions
    const transactions = [
      {
        amount: 45,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Food')._id,
        date: new Date('2023-10-01'),
        description: 'Grocery shopping',
      },
      {
        amount: 120,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Transportation')._id,
        date: new Date('2023-10-02'),
        description: 'Gas refill',
      },
      {
        amount: 60,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Entertainment')._id,
        date: new Date('2023-10-03'),
        description: 'Movie tickets',
      },
      {
        amount: 85,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Utilities')._id,
        date: new Date('2023-10-04'),
        description: 'Electricity bill',
      },
      {
        amount: 1200,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Rent')._id,
        date: new Date('2023-10-05'),
        description: 'Monthly rent',
      },
      {
        amount: 3500,
        type: 'income',
        category: createdCategories.find(cat => cat.name === 'Salary')._id,
        date: new Date('2023-10-06'),
        description: 'Monthly salary',
      },
      {
        amount: 200,
        type: 'income',
        category: createdCategories.find(cat => cat.name === 'Freelance')._id,
        date: new Date('2023-10-07'),
        description: 'Freelance design work',
      },
      {
        amount: 30,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Food')._id,
        date: new Date('2023-10-08'),
        description: 'Coffee and snacks',
      },
      {
        amount: 40,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Transportation')._id,
        date: new Date('2023-10-09'),
        description: 'Public transit pass',
      },
      {
        amount: 75,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Entertainment')._id,
        date: new Date('2023-10-10'),
        description: 'Streaming subscription',
      },
    ];

    await Transaction.insertMany(transactions);

    console.log('✅ Seed data successfully loaded!');
    mongoose.connection.close();
  } catch (error) {
    console.error('❌ Error seeding data:', error);
    mongoose.connection.close();
  }
};

seedData();