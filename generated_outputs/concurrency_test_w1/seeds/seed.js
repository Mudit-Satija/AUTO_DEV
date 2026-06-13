const mongoose = require('mongoose');
const Transaction = require('../models/Transaction');
const Budget = require('../models/Budget');
const Category = require('../models/Category');

const connectDB = require('../config/db');

const seedDatabase = async () => {
  try {
    await connectDB();

    // Clear existing data
    await Transaction.deleteMany({});
    await Budget.deleteMany({});
    await Category.deleteMany({});

    // Seed Categories
    const categories = [
      { name: 'Food', color: '#FF6B6B' },
      { name: 'Transportation', color: '#4ECDC4' },
      { name: 'Entertainment', color: '#45B7D1' },
      { name: 'Utilities', color: '#96CEB4' },
      { name: 'Healthcare', color: '#FFEAA7' },
      { name: 'Rent', color: '#DDA0DD' },
      { name: 'Salary', color: '#A8E6CF' },
      { name: 'Freelance', color: '#FDFFB6' }
    ];

    const createdCategories = await Category.insertMany(categories);

    // Seed Budgets
    const budgets = [
      {
        category: createdCategories.find(cat => cat.name === 'Food')?._id,
        amount: 500,
        month: '2024-01',
        spent: 320
      },
      {
        category: createdCategories.find(cat => cat.name === 'Transportation')?._id,
        amount: 200,
        month: '2024-01',
        spent: 180
      },
      {
        category: createdCategories.find(cat => cat.name === 'Entertainment')?._id,
        amount: 150,
        month: '2024-01',
        spent: 90
      },
      {
        category: createdCategories.find(cat => cat.name === 'Utilities')?._id,
        amount: 300,
        month: '2024-01',
        spent: 280
      },
      {
        category: createdCategories.find(cat => cat.name === 'Rent')?._id,
        amount: 1200,
        month: '2024-01',
        spent: 1200
      },
      {
        category: createdCategories.find(cat => cat.name === 'Salary')?._id,
        amount: 3500,
        month: '2024-01',
        spent: 3500
      }
    ];

    const createdBudgets = await Budget.insertMany(budgets);

    // Seed Transactions
    const transactions = [
      {
        description: 'Grocery shopping',
        amount: 120,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Food')?._id,
        date: new Date('2024-01-05')
      },
      {
        description: 'Gas refill',
        amount: 60,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Transportation')?._id,
        date: new Date('2024-01-07')
      },
      {
        description: 'Movie tickets',
        amount: 30,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Entertainment')?._id,
        date: new Date('2024-01-10')
      },
      {
        description: 'Electricity bill',
        amount: 120,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Utilities')?._id,
        date: new Date('2024-01-15')
      },
      {
        description: 'Rent payment',
        amount: 1200,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Rent')?._id,
        date: new Date('2024-01-01')
      },
      {
        description: 'Monthly salary',
        amount: 3500,
        type: 'income',
        category: createdCategories.find(cat => cat.name === 'Salary')?._id,
        date: new Date('2024-01-01')
      },
      {
        description: 'Freelance design work',
        amount: 400,
        type: 'income',
        category: createdCategories.find(cat => cat.name === 'Freelance')?._id,
        date: new Date('2024-01-12')
      },
      {
        description: 'Dinner with friends',
        amount: 80,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Food')?._id,
        date: new Date('2024-01-18')
      },
      {
        description: 'Bus pass',
        amount: 40,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Transportation')?._id,
        date: new Date('2024-01-20')
      },
      {
        description: 'Spotify subscription',
        amount: 15,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Entertainment')?._id,
        date: new Date('2024-01-22')
      },
      {
        description: 'Internet bill',
        amount: 80,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Utilities')?._id,
        date: new Date('2024-01-25')
      },
      {
        description: 'Doctor visit',
        amount: 100,
        type: 'expense',
        category: createdCategories.find(cat => cat.name === 'Healthcare')?._id,
        date: new Date('2024-01-28')
      }
    ];

    await Transaction.insertMany(transactions);

    console.log('Database seeded successfully!');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
};

seedDatabase();