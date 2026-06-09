import React from 'react';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  createdAt: string;
}

const Dashboard: React.FC = () => {
  // Mock data for demonstration
  const tasks: Task[] = [
    { id: '1', title: 'Complete project proposal', description: 'Draft and submit proposal for Q3', priority: 'high', completed: true, createdAt: '2024-01-15T10:00:00Z' },
    { id: '2', title: 'Review team feedback', description: 'Analyze feedback from sprint review', priority: 'medium', completed: false, createdAt: '2024-01-16T14:30:00Z' },
    { id: '3', title: 'Update documentation', description: 'Revise API docs for v2.1', priority: 'low', completed: true, createdAt: '2024-01-17T09:15:00Z' },
    { id: '4', title: 'Deploy new feature', description: 'Push feature to staging environment', priority: 'high', completed: false, createdAt: '2024-01-18T11:20:00Z' },
  ];

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.completed).length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const priorityCounts = {
    high: tasks.filter(task => task.priority === 'high').length,
    medium: tasks.filter(task => task.priority === 'medium').length,
    low: tasks.filter(task => task.priority === 'low').length,
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 shadow-md">
          <h2 className="text-lg font-medium text-gray-300">Total Tasks</h2>
          <p className="text-3xl font-bold mt-2">{totalTasks}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 shadow-md">
          <h2 className="text-lg font-medium text-gray-300">Completed</h2>
          <p className="text-3xl font-bold mt-2">{completedTasks}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 shadow-md">
          <h2 className="text-lg font-medium text-gray-300">Completion Rate</h2>
          <p className="text-3xl font-bold mt-2">{completionRate}%</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 shadow-md">
          <h2 className="text-lg font-medium text-gray-300">Pending</h2>
          <p className="text-3xl font-bold mt-2">{totalTasks - completedTasks}</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 shadow-md">
        <h2 className="text-2xl font-bold mb-6">Priority Overview</h2>
        <div className="flex flex-col space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-gray-300">High Priority</span>
            <span className="font-bold text-red-400">{priorityCounts.high}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div
              className="bg-red-500 h-2.5 rounded-full"
              style={{ width: `${(priorityCounts.high / totalTasks) * 100 || 0}%` }}
            ></div>
          </div>
        </div>

        <div className="flex flex-col space-y-4 mt-6">
          <div className="flex justify-between items-center">
            <span className="text-gray-300">Medium Priority</span>
            <span className="font-bold text-yellow-400">{priorityCounts.medium}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div
              className="bg-yellow-500 h-2.5 rounded-full"
              style={{ width: `${(priorityCounts.medium / totalTasks) * 100 || 0}%` }}
            ></div>
          </div>
        </div>

        <div className="flex flex-col space-y-4 mt-6">
          <div className="flex justify-between items-center">
            <span className="text-gray-300">Low Priority</span>
            <span className="font-bold text-green-400">{priorityCounts.low}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div
              className="bg-green-500 h-2.5 rounded-full"
              style={{ width: `${(priorityCounts.low / totalTasks) * 100 || 0}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;