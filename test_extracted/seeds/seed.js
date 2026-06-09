const mongoose = require('mongoose');
const connectDB = require('../backend/src/config/database');
const User = require('../backend/src/models/users');
const Task = require('../backend/src/models/tasks');

async function seed() {
  await connectDB();

  const users = [
    {
      username: 'admin',
      email: 'admin@example.com',
      password: '$2a$10$123456789012345678901eJ8u9Z0u9Z0u9Z0u9Z0u9Z0u9Z0u9Z0u', // password: password123
      role: 'admin'
    },
    {
      username: 'user',
      email: 'user@example.com',
      password: '$2a$10$123456789012345678901eJ8u9Z0u9Z0u9Z0u9Z0u9Z0u9Z0u9Z0u', // password: password123
      role: 'user'
    }
  ];

  await User.deleteMany({});
  await User.insertMany(users);

  const tasks = [
    {
      title: 'Complete Dashboard UI',
      description: 'Finish the dashboard layout and components',
      status: 'pending',
      priority: 'high',
      assignedTo: users[0]._id
    },
    {
      title: 'Implement Task Management',
      description: 'Add create, read, update, delete functionality for tasks',
      status: 'in-progress',
      priority: 'medium',
      assignedTo: users[1]._id
    },
    {
      title: 'Set up JWT Authentication',
      description: 'Configure JWT tokens for user sessions',
      status: 'completed',
      priority: 'high',
      assignedTo: users[0]._id
    }
  ];

  await Task.deleteMany({});
  await Task.insertMany(tasks);

  mongoose.connection.close();
}

seed().catch(console.error);