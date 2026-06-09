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
    { title: 'Complete project setup', description: 'Initialize Express and React apps', completed: false },
    { title: 'Design database schema', description: 'Define Task model with title and status', completed: false },
    { title: 'Create API endpoints', description: 'Implement GET and POST routes for tasks', completed: false }
  ];

  const completedTasks = [
    { title: 'Set up MongoDB connection', description: 'Connected database using Mongoose', completed: true },
    { title: 'Configure Express server', description: 'Started server on port 5000', completed: true },
    { title: 'Build React frontend', description: 'Created PendingTasks and CompletedTasks pages', completed: true }
  ];

  await Task.insertMany([...pendingTasks, ...completedTasks]);
  console.log('Seed data inserted successfully');

  mongoose.connection.close();
}

seed().catch(err => console.error(err));