const mongoose = require('mongoose');
const db = require('../src/config/database');

const seedData = async () => {
  try {
    await db.connect();

    const User = require('../src/models/users');
    const Task = require('../src/models/tasks');

    await User.deleteMany({});
    await Task.deleteMany({});

    const user = new User({
      username: 'testuser',
      email: 'test@example.com',
      password: '$2a$10$123456789012345678901uJq7Yf3L8R5H2K9w3X1Yz7V8b9c0dEeF' // hashed password for 'password123'
    });
    await user.save();

    const tasks = [
      {
        title: 'Complete Dashboard UI',
        description: 'Design and implement the dashboard page with React',
        status: 'pending',
        priority: 'high',
        assignedTo: user._id
      },
      {
        title: 'Implement Task Management API',
        description: 'Create REST endpoints for tasks CRUD operations',
        status: 'in-progress',
        priority: 'medium',
        assignedTo: user._id
      },
      {
        title: 'Set up JWT Authentication',
        description: 'Configure JWT token generation and verification',
        status: 'completed',
        priority: 'high',
        assignedTo: user._id
      }
    ];

    await Task.insertMany(tasks);

    console.log('Seed data inserted successfully');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding data:', error);
    process.exit(1);
  }
};

seedData();