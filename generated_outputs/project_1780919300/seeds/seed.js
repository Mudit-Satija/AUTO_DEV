const mongoose = require('mongoose');
const { connectDB } = require('../backend/src/config/database');
const User = require('../backend/src/models/users');
const Task = require('../backend/src/models/tasks');

const seedData = async () => {
  await connectDB();

  // Clear existing data
  await User.deleteMany({});
  await Task.deleteMany({});

  // Create sample users
  const user1 = new User({
    username: 'john_doe',
    email: 'john@example.com',
    password: '$2a$10$examplehashedpassword123456789012345678901234567890123456789012345' // hashed password for testing
  });

  const user2 = new User({
    username: 'jane_smith',
    email: 'jane@example.com',
    password: '$2a$10$examplehashedpassword987654321098765432109876543210987654321098765' // hashed password for testing
  });

  await Promise.all([user1.save(), user2.save()]);

  // Create sample tasks
  const task1 = new Task({
    title: 'Complete dashboard UI',
    description: 'Design and implement the main dashboard page with charts and stats',
    assignedTo: user1._id,
    status: 'pending',
    priority: 'high'
  });

  const task2 = new Task({
    title: 'Implement task management API',
    description: 'Create CRUD endpoints for tasks with JWT authentication',
    assignedTo: user2._id,
    status: 'in-progress',
    priority: 'high'
  });

  const task3 = new Task({
    title: 'Write unit tests',
    description: 'Write tests for all backend routes and models',
    assignedTo: user1._id,
    status: 'completed',
    priority: 'medium'
  });

  await Promise.all([task1.save(), task2.save(), task3.save()]);

  console.log('Seed data successfully inserted');
  process.exit();
};

seedData().catch(err => {
  console.error('Error seeding data:', err);
  process.exit(1);
});