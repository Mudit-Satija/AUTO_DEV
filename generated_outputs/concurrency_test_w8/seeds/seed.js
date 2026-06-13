const mongoose = require('mongoose');
const Transaction = require('../models/Transaction');
const Budget = require('../models/Budget');
const Category = require('../models/Category');

const seedDatabase = async () => {
  try {
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
      { name: 'Entertainment', color: '#45B7D1' },
      { name: 'Utilities', color: '#96CEB4' },
      { name: 'Healthcare', color: '#FFEAA7' },
      { name: 'Education', color: '#DDA0DD' },
      { name: 'Rent', color: '#F7DC6F' },
      { name: 'Salary', color: '#BB8FCE' },
      { name: 'Freelance', color: '#82CCDD' },
    ];

    const createdCategories = await Category.insertMany(categories);

    // Seed Budgets
    const budgets = [
      {
        category: createdCategories.find(cat => cat.name === 'Food')?._id,
        amount: 500,
        month: '2024-05',
        spent: 320,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Transportation')?._id,
        amount: 200,
        month: '2024-05',
        spent: 180,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Entertainment')?._id,
        amount: 150,
        month: '2024-05',
        spent: 90,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Utilities')?._id,
        amount: 300,
        month: '2024-05',
        spent: 280,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Rent')?._id,
        amount: 1200,
        month: '2024-05',
        spent: 1200,
      },
      {
        category: createdCategories.find(cat => cat.name === 'Salary')?._id,
        amount: 4000,
        month: '2024-05',
        spent: 4000,
      },
    ];

    await Budget.insertMany(budgets);

    // Seed Transactions
    const transactions = [
      {
        amount: 45,
        category: createdCategories.find(cat => cat.name === 'Food')?._id,
        description: 'Grocery shopping',
        date: new Date('2024-05-01'),
        type: 'expense',
      },
      {
        amount: 60,
        category: createdCategories.find(cat => cat.name === 'Food')?._id,
        description: 'Restaurant dinner',
        date: new Date('2024-05-03'),
        type: 'expense',
      },
      {
        amount: 80,
        category: createdCategories.find(cat => cat.name === 'Transportation')?._id,
        description: 'Gas refill',
        date: new Date('2024-05-02'),
        type: 'expense',
      },
      {
        amount: 120,
        category: createdCategories.find(cat => cat.name === 'Entertainment')?._id,
        description: 'Movie tickets',
        date: new Date('2024-05-05'),
        type: 'expense',
      },
      {
        amount: 150,
        category: createdCategories.find(cat => cat.name === 'Utilities')?._id,
        description: 'Electricity bill',
        date: new Date('2024-05-04'),
        type: 'expense',
      },
      {
        amount: 4000,
        category: createdCategories.find(cat => cat.name === 'Salary')?._id,
        description: 'Monthly salary',
        date: new Date('2024-05-01'),
        type: 'income',
      },
      {
        amount: 200,
        category: createdCategories.find(cat => cat.name === 'Freelance')?._id,
        description: 'Freelance design work',
        date: new Date('2024-05-10'),
        type: 'income',
      },
      {
        amount: 30,
        category: createdCategories.find(cat => cat.name === 'Food')?._id,
        description: 'Coffee & snacks',
        date: new Date('2024-05-07'),
        type: 'expense',
      },
      {
        amount: 75,
        category: createdCategories.find(cat => cat.name === 'Transportation')?._id,
        description: 'Ride-share',
        date: new Date('2024-05-08'),
        type: 'expense',
      },
      {
        amount: 45,
        category: createdCategories.find(cat => cat.name === 'Entertainment')?._id,
        description: 'Streaming subscription',
        date: new Date('2024-05-12'),
        type: 'expense',
      },
    ];

    await Transaction.insertMany(transactions);

    console.log('✅ Database seeded successfully!');
    mongoose.connection.close();
  } catch (error) {
    console.error('❌ Error seeding database:', error);
    mongoose.connection.close();
  }
};

seedDatabase();