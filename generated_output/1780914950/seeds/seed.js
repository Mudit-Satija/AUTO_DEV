const mongoose = require('mongoose');
const connectDB = require('../backend/src/config/database');
const Task = require('../backend/src/models/tasks');
const Categorie = require('../backend/src/models/categories');

async function seed() {
  await connectDB();

  await Task.deleteMany({});
  await Categorie.deleteMany({});

  const categories = [
    { name: 'Work' },
    { name: 'Personal' },
    { name: 'Shopping' },
    { name: 'Health' }
  ];

  await Categorie.insertMany(categories);

  const tasks = [
    { title: 'Complete project proposal', description: 'Draft and submit project proposal for Q3', categoryId: (await Categorie.findOne({ name: 'Work' }))._id, completed: false },
    { title: 'Grocery shopping', description: 'Buy milk, bread, eggs, and vegetables', categoryId: (await Categorie.findOne({ name: 'Shopping' }))._id, completed: true },
    { title: 'Morning workout', description: '30 minutes cardio and strength training', categoryId: (await Categorie.findOne({ name: 'Health' }))._id, completed: false },
    { title: 'Call dentist', description: 'Schedule annual checkup', categoryId: (await Categorie.findOne({ name: 'Health' }))._id, completed: false },
    { title: 'Read new book', description: 'Finish reading "Atomic Habits"', categoryId: (await Categorie.findOne({ name: 'Personal' }))._id, completed: false },
    { title: 'Update resume', description: 'Revise resume with latest experience', categoryId: (await Categorie.findOne({ name: 'Work' }))._id, completed: true }
  ];

  await Task.insertMany(tasks);

  console.log('Seed data inserted successfully');
  mongoose.connection.close();
}

seed().catch(err => console.error(err));