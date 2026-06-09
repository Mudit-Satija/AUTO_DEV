const mongoose = require('mongoose');
const connectDB = require('../backend/src/config/database');

const taskSchema = new mongoose.Schema({
  title: String,
  description: String,
  status: String,
  createdAt: Date,
  updatedAt: Date
});

const Task = mongoose.model('Task', taskSchema);

async function seed() {
  await connectDB();

  const tasks = [
    {
      title: 'Complete Dashboard UI',
      description: 'Design and implement the main dashboard layout with task cards and filters',
      status: 'completed',
      createdAt: new Date('2023-10-01T08:00:00Z'),
      updatedAt: new Date('2023-10-01T12:00:00Z')
    },
    {
      title: 'Create Task Form',
      description: 'Build a form to add new tasks with title, description, and due date',
      status: 'completed',
      createdAt: new Date('2023-10-02T09:00:00Z'),
      updatedAt: new Date('2023-10-02T11:30:00Z')
    },
    {
      title: 'Task Details Page',
      description: 'Develop a detailed view for individual tasks with edit and delete options',
      status: 'in-progress',
      createdAt: new Date('2023-10-03T10:00:00Z'),
      updatedAt: new Date('2023-10-04T14:20:00Z')
    },
    {
      title: 'Completed Tasks Archive',
      description: 'Implement a section to view and filter all completed tasks',
      status: 'completed',
      createdAt: new Date('2023-10-04T13:00:00Z'),
      updatedAt: new Date('2023-10-04T16:00:00Z')
    },
    {
      title: 'API Endpoint for Tasks',
      description: 'Create REST endpoints to handle CRUD operations for tasks',
      status: 'in-progress',
      createdAt: new Date('2023-10-05T08:30:00Z'),
      updatedAt: new Date('2023-10-05T10:45:00Z')
    },
    {
      title: 'Responsive Design for Mobile',
      description: 'Ensure all pages are fully responsive and work on mobile devices',
      status: 'todo',
      createdAt: new Date('2023-10-06T09:15:00Z'),
      updatedAt: new Date('2023-10-06T09:15:00Z')
    }
  ];

  await Task.deleteMany({});
  await Task.insertMany(tasks);

  console.log('Seed data inserted successfully');
  mongoose.connection.close();
}

seed().catch(console.error);