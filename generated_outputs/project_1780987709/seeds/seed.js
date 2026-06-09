const mongoose = require('mongoose');
const connectDB = require('../backend/src/config/database');

const taskSchema = new mongoose.Schema({
  title: String,
  description: String,
  completed: Boolean,
  createdAt: { type: Date, default: Date.now }
});

const Task = mongoose.model('Task', taskSchema);

async function seed() {
  await connectDB();

  const pendingTasks = [
    { title: 'Complete project setup', description: 'Initialize Express and React projects', completed: false },
    { title: 'Design UI components', description: 'Create layout for PendingTasks and CompletedTasks pages', completed: false },
    { title: 'Connect MongoDB', description: 'Establish database connection and model schemas', completed: false }
  ];

  const completedTasks = [
    { title: 'Set up development environment', description: 'Install Node.js, MongoDB, and dependencies', completed: true },
    { title: 'Create basic route structure', description: 'Define API endpoints for tasks', completed: true }
  ];

  await Task.insertMany([...pendingTasks, ...completedTasks]);
  console.log('Seed data inserted successfully');

  mongoose.connection.close();
}

seed().catch(console.error);