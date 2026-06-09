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

  const createdCategories = await Categorie.insertMany(categories);

  const tasks = [
    { title: 'Complete project proposal', description: 'Draft and submit project proposal for client', category: createdCategories[0]._id, completed: false },
    { title: 'Gym workout', description: '30 minutes cardio and strength training', category: createdCategories[3]._id, completed: true },
    { title: 'Buy groceries', description: 'Milk, eggs, bread, vegetables', category: createdCategories[2]._id, completed: false },
    { title: 'Call dentist', description: 'Schedule annual checkup', category: createdCategories[3]._id, completed: false },
    { title: 'Review team feedback', description: 'Analyze sprint feedback from team members', category: createdCategories[0]._id, completed: true },
    { title: 'Plan weekend trip', description: 'Research destinations and book accommodations', category: createdCategories[1]._id, completed: false }
  ];

  await Task.insertMany(tasks);

  console.log('Seed data inserted successfully');
  mongoose.connection.close();
}

seed().catch(console.error);