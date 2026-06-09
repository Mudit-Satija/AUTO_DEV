import React from 'react';

interface TaskStats {
  total: number;
  completed: number;
  pending: number;
  highPriority: number;
  mediumPriority: number;
  lowPriority: number;
}

const Dashboard: React.FC = () => {
  const stats: TaskStats = {
    total: 12,
    completed: 8,
    pending: 4,
    highPriority: 3,
    mediumPriority: 5,
    lowPriority: 4,
  };

  const completionRate = Math.round((stats.completed / stats.total) * 100);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-medium text-gray-400">Total Tasks</h2>
          <p className="text-3xl font-bold">{stats.total}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-medium text-gray-400">Completed</h2>
          <p className="text-3xl font-bold">{stats.completed}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-medium text-gray-400">Pending</h2>
          <p className="text-3xl font-bold">{stats.pending}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-medium text-gray-400">Completion Rate</h2>
          <p className="text-3xl font-bold">{completionRate}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-bold mb-4">Priority Overview</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-300">High</span>
              <span className="font-bold">{stats.highPriority}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">Medium</span>
              <span className="font-bold">{stats.mediumPriority}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">Low</span>
              <span className="font-bold">{stats.lowPriority}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 shadow-lg lg:col-span-2">
          <h2 className="text-xl font-bold mb-4">Summary Metrics</h2>
          <div className="flex flex-col space-y-4">
            <div className="flex items-center">
              <div className="w-full bg-gray-700 rounded-full h-2.5 mr-4">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full" 
                  style={{ width: `${completionRate}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-300">{completionRate}% completed</span>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-300">Average task age: 3 days</span>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-300">Tasks overdue: 2</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;