import React from 'react';

const Dashboard: React.FC = () => {
  const taskStats = {
    total: 12,
    completed: 8,
    pending: 4,
    highPriority: 3,
    mediumPriority: 5,
    lowPriority: 4,
  };

  const completionRate = Math.round((taskStats.completed / taskStats.total) * 100);

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-white">Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h3 className="text-gray-400 text-sm font-medium">Total Tasks</h3>
          <p className="text-3xl font-bold text-white">{taskStats.total}</p>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h3 className="text-gray-400 text-sm font-medium">Completed</h3>
          <p className="text-3xl font-bold text-green-400">{taskStats.completed}</p>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h3 className="text-gray-400 text-sm font-medium">Pending</h3>
          <p className="text-3xl font-bold text-yellow-400">{taskStats.pending}</p>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h3 className="text-gray-400 text-sm font-medium">Completion Rate</h3>
          <p className="text-3xl font-bold text-blue-400">{completionRate}%</p>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-bold text-white mb-4">Priority Overview</h3>
        <div className="flex flex-col space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-300">High Priority</span>
            <span className="text-red-400 font-medium">{taskStats.highPriority}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300">Medium Priority</span>
            <span className="text-yellow-400 font-medium">{taskStats.mediumPriority}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300">Low Priority</span>
            <span className="text-green-400 font-medium">{taskStats.lowPriority}</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-bold text-white mb-4">Recent Activity</h3>
        <ul className="space-y-2 text-gray-300">
          <li>• Task "Complete project proposal" marked as complete</li>
          <li>• New task "Review design mockups" added</li>
          <li>• Task "Schedule team meeting" updated</li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;