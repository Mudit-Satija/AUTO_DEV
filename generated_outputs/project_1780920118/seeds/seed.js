const mongoose = require('mongoose');
const connectDB = require('../backend/src/config/database');
const Task = require('../backend/src/models/tasks');

async function seed() {
  await connectDB();

  const tasks = [
    {
      title: 'Complete project proposal',
      description: 'Draft and submit the project proposal for client review',
      status: 'pending',
      createdAt: new Date('2023-10-01T08:00:00Z'),
      updatedAt: new Date('2023-10-01T08:00:00Z')
    },
    {
      title: 'Review team feedback',
      description: 'Analyze feedback from team members on the design prototype',
      status: 'pending',
      createdAt: new Date('2023-10-02T09:30:00Z'),
      updatedAt: new Date('2023-10-02T09:30:00Z')
    },
    {
      title: 'Deploy staging environment',
      description: 'Set up and verify the staging server for the new feature',
      status: 'completed',
      createdAt: new Date('2023-09-28T14:15:00Z'),
      updatedAt: new Date('2023-09-28T16:45:00Z')
    },
    {
      title: 'Update documentation',
      description: 'Revise API documentation to reflect recent changes',
      status: 'completed',
      createdAt: new Date('2023-09-29T10:00:00Z'),
      updatedAt: new Date('2023-09-29T11:30:00Z')
    }
  ];

  await Task.deleteMany({});
  await Task.insertMany(tasks);

  mongoose.connection.close();
}

seed().catch(console.error);