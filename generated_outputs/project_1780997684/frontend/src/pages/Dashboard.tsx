import { useState, useEffect } from 'react';

const Dashboard = () => {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    // In a real app, this would fetch from API
    // For now, mock data
    setTasks([
      { id: 1, title: 'Complete project', priority: 'high', completed: false },
      { id: 2, title: 'Review code', priority: 'medium', completed: true },
      { id: 3, title: 'Update documentation', priority: 'low', completed: true },
    ]);
  }, []);

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.completed).length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const priorityCounts = {
    high: tasks.filter(t => t.priority === 'high').length,
    medium: tasks.filter(t => t.priority === 'medium').length,
    low: tasks.filter(t => t.priority === 'low').length,
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-medium text-gray-300">Total Tasks</h2>
          <p className="text-3xl font-bold mt-2">{totalTasks}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-medium text-gray-300">Completed</h2>
          <p className="text-3xl font-bold mt-2">{completedTasks}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-medium text-gray-300">Completion Rate</h2>
          <p className="text-3xl font-bold mt-2">{completionRate}%</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-medium text-gray-300">Active Tasks</h2>
          <p className="text-3xl font-bold mt-2">{totalTasks - completedTasks}</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 shadow-lg mb-8">
        <h2 className="text-2xl font-bold mb-6">Priority Overview</h2>
        <div className="flex space-x-6">
          <div className="flex-1 text-center">
            <div className="text-2xl font-bold text-red-500">{priorityCounts.high}</div>
            <div className="text-gray-300">High Priority</div>
          </div>
          <div className="flex-1 text-center">
            <div className="text-2xl font-bold text-yellow-500">{priorityCounts.medium}</div>
            <div className="text-gray-300">Medium Priority</div>
          </div>
          <div className="flex-1 text-center">
            <div className="text-2xl font-bold text-green-500">{priorityCounts.low}</div>
            <div className="text-gray-300">Low Priority</div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
        <h2 className="text-2xl font-bold mb-6">Recent Tasks</h2>
        <ul className="space-y-3">
          {tasks.slice(0, 5).map(task => (
            <li key={task.id} className="flex justify-between items-center p-3 bg-gray-700 rounded">
              <span>{task.title}</span>
              <span className={`px-2 py-1 text-xs rounded-full ${
                task.priority === 'high' ? 'bg-red-600' :
                task.priority === 'medium' ? 'bg-yellow-600' :
                'bg-green-600'
              }`}>
                {task.priority}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;