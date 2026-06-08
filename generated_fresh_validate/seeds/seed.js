const mongoose = require('mongoose');
const connectDB = require('../backend/src/config/database');
const Users = require('../backend/src/models/users');
const Tasks = require('../backend/src/models/tasks');
const Categories = require('../backend/src/models/categories');

async function seedDatabase() {
  await connectDB();

  const defaultUser = await Users.create({
    username: 'admin',
    email: 'admin@example.com',
    password: '$2a$10$123456789012345678901eJ8Q6R4V5U7W8X9Y0Z1A2B3C4D5E6F7', // hashed 'password'
  });

  const defaultCategory = await Categories.create({
    name: 'Work',
    userId: defaultUser._id,
  });

  const defaultTask = await Tasks.create({
    title: 'Complete project setup',
    description: 'Set up Express, React, MongoDB, and JWT auth',
    completed: false,
    userId: defaultUser._id,
    categoryId: defaultCategory._id,
  });

  console.log('Seed data inserted successfully.');

  await mongoose.connection.close();
}

seedDatabase().catch(console.error);